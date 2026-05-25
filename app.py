
from __future__ import annotations

import math
from datetime import datetime
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
REST_STOPS_PATH = DATA_DIR / "rest_stops.csv"
MENUS_PATH = DATA_DIR / "menu_items.csv"
STORES_PATH = DATA_DIR / "stores.csv"
RATINGS_PATH = DATA_DIR / "ratings.csv"

st.set_page_config(
    page_title="Korean Highway Rest Stop Food Dashboard",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    .small-muted {color: #6b7280; font-size: 0.9rem; line-height: 1.45;}
    .badge {display:inline-block; padding:0.18rem 0.58rem; border-radius:999px; background:#f3f4f6; margin:0 0.35rem 0.35rem 0; font-size:0.82rem;}
    .focus-badge {background:#fff7ed; color:#9a3412; border:1px solid #fed7aa;}
    .signature-card {border:1px solid #e5e7eb; border-radius:18px; padding:1rem; background:white; box-shadow:0 1px 8px rgba(0,0,0,0.04); margin-bottom:0.7rem;}
    .metric-card {border:1px solid #e5e7eb; border-radius:16px; padding:0.9rem 1rem; background:#ffffff; min-height: 92px;}
    .metric-label {color:#6b7280; font-size:0.82rem;}
    .metric-value {font-weight:700; font-size:1.22rem; margin-top:0.16rem;}
    .menu-card {border:1px solid #e5e7eb; border-radius:16px; padding:0.9rem 1rem; background:#ffffff; margin-bottom:0.6rem;}
    .menu-card h4 {margin:0.25rem 0 0.25rem 0;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rest_stops = pd.read_csv(REST_STOPS_PATH)
    menus = pd.read_csv(MENUS_PATH)
    stores = pd.read_csv(STORES_PATH)

    if RATINGS_PATH.exists():
        ratings = pd.read_csv(RATINGS_PATH)
    else:
        ratings = pd.DataFrame(columns=["created_at", "rest_stop_id", "rating", "comment"])

    return rest_stops, menus, stores, ratings


def format_krw(value) -> str:
    try:
        return f"₩{int(float(value)):,}"
    except Exception:
        return str(value)


def bool_badge(value: str) -> str:
    return "Yes" if str(value).lower() in ["yes", "true", "1"] else "No"


def nearest_rest_stop(lat: float | None, lon: float | None, df: pd.DataFrame) -> str | None:
    if lat is None or lon is None or df.empty:
        return None
    distances = ((df["latitude"] - lat) ** 2 + (df["longitude"] - lon) ** 2) ** 0.5
    idx = distances.idxmin()
    return str(df.loc[idx, "rest_stop_id"])


def show_metric_card(label: str, value: str, caption: str | None = None) -> None:
    caption_html = f"<div class='small-muted'>{caption}</div>" if caption else ""
    st.markdown(
        f"""
        <div class='metric-card'>
          <div class='metric-label'>{label}</div>
          <div class='metric-value'>{value}</div>
          {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_popup_html(row: pd.Series, menus: pd.DataFrame, stores: pd.DataFrame) -> str:
    rest_id = row["rest_stop_id"]
    top_menus = menus[menus["rest_stop_id"] == rest_id].sort_values(
        ["is_signature", "recommended", "sample_rating"], ascending=[False, False, False]
    ).head(4)
    store_preview = stores[stores["rest_stop_id"] == rest_id].head(3)

    store_html = "".join(
        f"<div style='margin:4px 0;'>• <b>{s.food_area}</b> <span style='color:#555;'>({s.operating_hours})</span></div>"
        for s in store_preview.itertuples()
    )
    menu_html = "".join(
        f"<div style='margin:4px 0;'>• {m.menu_item} <b>{format_krw(m.price_krw)}</b></div>"
        for m in top_menus.itertuples()
    )

    return f"""
    <div style="
        width: 380px;
        font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', 'Noto Sans KR', Arial, sans-serif;
        font-size: 15px;
        line-height: 1.52;
        color: #111827;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    ">
      <h3 style="margin:0 0 6px 0; font-size:19px; line-height:1.3;">{row['display_name']}</h3>
      <div style="color:#4b5563; margin-bottom:8px;">{row['highway_route']} · {row['region']}</div>
      <div style="margin-bottom:8px;"><b>General Hours</b> · {row['general_hours']}</div>
      <div style="margin:8px 0 4px 0; font-weight:700;">Food Areas</div>
      {store_html}
      <div style="margin:10px 0 4px 0; font-weight:700;">Menu Preview</div>
      {menu_html}
      <div style="margin-top:10px; color:#6b7280; font-size:13px;">Click marker → full detail panel updates beside the map.</div>
    </div>
    """


def build_map(rest_df: pd.DataFrame, menus: pd.DataFrame, stores: pd.DataFrame) -> folium.Map:
    center = [36.35, 127.8] if rest_df.empty else [rest_df["latitude"].mean(), rest_df["longitude"].mean()]
    fmap = folium.Map(location=center, zoom_start=7, tiles="CartoDB positron", control_scale=True)

    for _, row in rest_df.iterrows():
        is_high = row["traffic_group"] == "High-traffic"
        radius = 10 if is_high else 7
        color = "red" if is_high else "blue"
        tooltip = f"{row['display_name']} · {row['highway_route']}"
        popup = folium.Popup(build_popup_html(row, menus, stores), max_width=430)
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=radius,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.76,
            tooltip=tooltip,
            popup=popup,
        ).add_to(fmap)

    return fmap


def menu_table(df: pd.DataFrame) -> None:
    show = df.copy()
    show["Price"] = show["price_krw"].apply(format_krw)
    show = show.rename(
        columns={
            "food_area": "Food Area / Store",
            "menu_item": "Menu Item",
            "food_category": "Food Category",
            "availability": "Available Time",
            "is_signature": "Signature Food",
            "recommended": "Recommended",
            "sample_rating": "Sample Rating",
            "menu_description": "Menu Description",
        }
    )
    cols = [
        "Food Area / Store",
        "Menu Item",
        "Food Category",
        "Price",
        "Available Time",
        "Signature Food",
        "Recommended",
        "Sample Rating",
        "Menu Description",
    ]
    st.dataframe(show[cols], use_container_width=True, hide_index=True)


def store_table(df: pd.DataFrame) -> None:
    show = df.copy().rename(
        columns={
            "food_area": "Food Area / Store",
            "store_type": "Restaurant Type",
            "description": "What You Can Find",
            "operating_hours": "Opening Hours",
        }
    )
    st.dataframe(
        show[["Food Area / Store", "Restaurant Type", "What You Can Find", "Opening Hours"]],
        use_container_width=True,
        hide_index=True,
    )


def show_signature_cards(selected_menus: pd.DataFrame) -> None:
    signatures = selected_menus[selected_menus["is_signature"].astype(str).str.lower().eq("yes")]
    if signatures.empty:
        st.info("No signature food is marked for this rest stop yet.")
        return
    for menu in signatures.sort_values("sample_rating", ascending=False).itertuples():
        rec_badge = "<span class='badge focus-badge'>Recommended</span>" if str(menu.recommended).lower() == "yes" else ""
        st.markdown(
            f"""
            <div class='signature-card'>
              <span class='badge focus-badge'>Signature Food</span>
              {rec_badge}
              <span class='badge'>{menu.food_category}</span>
              <h4>{menu.menu_item}</h4>
              <div class='small-muted'>{menu.food_area} · {menu.availability} · ⭐ {menu.sample_rating}</div>
              <p style='margin:0.6rem 0;'>{menu.menu_description}</p>
              <b>{format_krw(menu.price_krw)}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_menu_cards(selected_menus: pd.DataFrame) -> None:
    top_menus = selected_menus.sort_values(["is_signature", "recommended", "sample_rating"], ascending=[False, False, False]).head(6)
    for menu in top_menus.itertuples():
        badges = ""
        if str(menu.is_signature).lower() == "yes":
            badges += "<span class='badge focus-badge'>Signature</span>"
        if str(menu.recommended).lower() == "yes":
            badges += "<span class='badge'>Recommended</span>"
        badges += f"<span class='badge'>{menu.food_category}</span>"
        st.markdown(
            f"""
            <div class='menu-card'>
              {badges}
              <h4>{menu.menu_item} <span style='float:right;'>{format_krw(menu.price_krw)}</span></h4>
              <div class='small-muted'>{menu.food_area} · {menu.availability} · ⭐ {menu.sample_rating}</div>
              <p style='margin:0.55rem 0 0 0;'>{menu.menu_description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def save_rating(rest_stop_id: str, rating: int, comment: str) -> None:
    RATINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_row = pd.DataFrame(
        [{"created_at": datetime.now().isoformat(timespec="seconds"), "rest_stop_id": rest_stop_id, "rating": rating, "comment": comment}]
    )
    if RATINGS_PATH.exists():
        existing = pd.read_csv(RATINGS_PATH)
        updated = pd.concat([existing, new_row], ignore_index=True)
    else:
        updated = new_row
    updated.to_csv(RATINGS_PATH, index=False)
    st.cache_data.clear()


def render_detail(selected_id: str, rest_stops: pd.DataFrame, menus: pd.DataFrame, stores: pd.DataFrame, ratings: pd.DataFrame) -> None:
    selected = rest_stops[rest_stops["rest_stop_id"] == selected_id].iloc[0]
    selected_menus = menus[menus["rest_stop_id"] == selected_id].copy()
    selected_stores = stores[stores["rest_stop_id"] == selected_id].copy()
    selected_ratings = ratings[ratings["rest_stop_id"] == selected_id].copy() if not ratings.empty else ratings

    st.subheader(f"📍 {selected['display_name']}")
    focus_label = "High-traffic rest stop" if selected["traffic_group"] == "High-traffic" else "Additional national rest stop"
    st.markdown(
        f"<span class='badge focus-badge'>{focus_label}</span><span class='badge'>{selected['highway_route']}</span><span class='badge'>{selected['region']}</span>",
        unsafe_allow_html=True,
    )
    st.caption(selected["short_description"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        show_metric_card("Direction", str(selected["direction"]), "Driving direction")
    with c2:
        show_metric_card("Operating Hours", str(selected["general_hours"]), "Main food service")
    with c3:
        avg_price = selected_menus["price_krw"].mean() if not selected_menus.empty else 0
        show_metric_card("Average Price", format_krw(avg_price), "Selected rest stop")
    with c4:
        if not selected_ratings.empty and selected_ratings["rating"].notna().any():
            avg_rating = selected_ratings["rating"].astype(float).mean()
            show_metric_card("Traveler Rating", f"⭐ {avg_rating:.1f}", f"{len(selected_ratings)} saved rating(s)")
        else:
            show_metric_card("Sample Rating", f"⭐ {selected_menus['sample_rating'].mean():.1f}", "Seed menu average")

    detail_tab, menu_tab, store_tab, rating_tab = st.tabs(["Overview", "Menus & Prices", "Food Areas & Hours", "Rate This Stop"])

    with detail_tab:
        st.markdown("### Signature Menu")
        show_signature_cards(selected_menus)
        st.markdown("### Recommended Menu Preview")
        show_menu_cards(selected_menus)

    with menu_tab:
        st.markdown("### Full Menu Table")
        menu_table(selected_menus)
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            category_counts = selected_menus.groupby("food_category", as_index=False).size()
            fig = px.pie(category_counts, names="food_category", values="size", title="Menu Category Mix", hole=0.42)
            st.plotly_chart(fig, use_container_width=True)
        with chart_col2:
            price_df = selected_menus.sort_values("price_krw", ascending=True)
            fig = px.bar(
                price_df,
                x="price_krw",
                y="menu_item",
                color="food_category",
                orientation="h",
                title="Menu Price Comparison",
                labels={"price_krw": "Price (KRW)", "menu_item": "Menu Item", "food_category": "Food Category"},
            )
            st.plotly_chart(fig, use_container_width=True)

    with store_tab:
        st.markdown("### Restaurant Types and Opening Hours")
        store_table(selected_stores)
        type_counts = selected_stores.groupby("store_type", as_index=False).size()
        fig = px.bar(
            type_counts,
            x="store_type",
            y="size",
            title="Food Area Types in This Rest Stop",
            labels={"store_type": "Restaurant Type", "size": "Count"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with rating_tab:
        st.markdown("### Leave a Quick Rating")
        rating_value = st.slider("Your rating", min_value=1, max_value=5, value=4, step=1)
        rating_comment = st.text_input("Short comment", placeholder="e.g. Food was quick and convenient.")
        if st.button("Save Rating", type="primary"):
            save_rating(selected_id, rating_value, rating_comment)
            st.success("Rating saved locally.")
            st.rerun()

        if not selected_ratings.empty:
            show = selected_ratings.rename(columns={"created_at": "Submitted At", "rating": "Rating", "comment": "Comment"})
            st.dataframe(show[["Submitted At", "Rating", "Comment"]].tail(10), use_container_width=True, hide_index=True)
        else:
            st.info("No saved ratings yet for this rest stop.")


def render_dashboard() -> None:
    rest_stops, menus, stores, ratings = load_data()

    st.title("🍜 Korean Highway Rest Stop Food Dashboard")
    st.caption("A national map-based dashboard for rest stop food areas, menus, prices, hours, and traveler ratings.")

    with st.sidebar:
        st.header("Controls")
        view_mode = st.radio("Dashboard View", ["교통량 많은 휴게소", "전부 보기"], index=0)
        route_options = ["All routes"] + sorted(rest_stops["highway_route"].dropna().unique().tolist())
        selected_route = st.selectbox("Highway Route", route_options)
        region_options = ["All regions"] + sorted(rest_stops["region"].dropna().unique().tolist())
        selected_region = st.selectbox("Region", region_options)
        category_options = ["All food categories"] + sorted(menus["food_category"].dropna().unique().tolist())
        selected_category = st.selectbox("Food Category", category_options)
        keyword = st.text_input("Search", placeholder="휴게소명 또는 메뉴명을 입력하세요")
        st.markdown("---")
        st.markdown("**Marker guide**")
        st.caption("Red = high-traffic rest stop / Blue = additional national rest stop")

    filtered = rest_stops.copy()
    if view_mode == "교통량 많은 휴게소":
        filtered = filtered[filtered["traffic_group"] == "High-traffic"]
    if selected_route != "All routes":
        filtered = filtered[filtered["highway_route"] == selected_route]
    if selected_region != "All regions":
        filtered = filtered[filtered["region"] == selected_region]
    if selected_category != "All food categories":
        ids = menus[menus["food_category"] == selected_category]["rest_stop_id"].unique()
        filtered = filtered[filtered["rest_stop_id"].isin(ids)]
    if keyword.strip():
        q = keyword.strip().lower()
        menu_ids = menus[menus["menu_item"].str.lower().str.contains(q, na=False)]["rest_stop_id"].unique()
        filtered = filtered[
            filtered["rest_stop_name"].str.lower().str.contains(q, na=False)
            | filtered["display_name"].str.lower().str.contains(q, na=False)
            | filtered["rest_stop_id"].isin(menu_ids)
        ]

    if filtered.empty:
        st.warning("No rest stops match your current filters.")
        return

    visible_menus = menus[menus["rest_stop_id"].isin(filtered["rest_stop_id"])]
    visible_stores = stores[stores["rest_stop_id"].isin(filtered["rest_stop_id"])]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        show_metric_card("Rest Stops Shown", f"{len(filtered):,}", view_mode)
    with m2:
        show_metric_card("Menu Items", f"{len(visible_menus):,}", "Visible dataset")
    with m3:
        show_metric_card("Food Areas", f"{len(visible_stores):,}", "Restaurants and store areas")
    with m4:
        show_metric_card("Signature Foods", f"{(visible_menus['is_signature'] == 'Yes').sum():,}", "Separated from general menus")

    map_col, detail_col = st.columns([1.18, 1.0], gap="large")

    with map_col:
        st.subheader("🗺️ Map View")
        st.write("Click a marker to preview menus on the map and update the full detail panel.")
        fmap = build_map(filtered, menus, stores)
        map_data = st_folium(fmap, height=575, use_container_width=True, returned_objects=["last_object_clicked"])
        clicked_id = None
        if map_data and map_data.get("last_object_clicked"):
            clicked = map_data["last_object_clicked"]
            clicked_id = nearest_rest_stop(clicked.get("lat"), clicked.get("lng"), filtered)

    with detail_col:
        st.subheader("Selected Rest Stop")
        default_id = clicked_id or filtered.iloc[0]["rest_stop_id"]
        labels = (filtered["display_name"] + " · " + filtered["highway_route"]).tolist()
        label_to_id = dict(zip(labels, filtered["rest_stop_id"]))
        id_to_label = {v: k for k, v in label_to_id.items()}
        default_idx = labels.index(id_to_label[default_id]) if default_id in id_to_label else 0
        selected_label = st.selectbox("Select manually or click a map marker", labels, index=default_idx)
        selected_id = label_to_id[selected_label]
        render_detail(selected_id, rest_stops, menus, stores, ratings)

    st.markdown("---")
    analytics_tab, data_tab, source_tab = st.tabs(["National Analytics", "Complete Dataset", "Source Notes"])
    with analytics_tab:
        left, right = st.columns(2)
        with left:
            traffic_df = filtered.copy()
            traffic_df["Traffic Focus"] = traffic_df["traffic_group"].replace({"High-traffic": "High-traffic", "Regular": "Additional"})
            fig = px.histogram(
                traffic_df,
                x="highway_route",
                color="Traffic Focus",
                title="Rest Stops by Highway Route",
                labels={"highway_route": "Highway Route"},
            )
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            avg_by_route = visible_menus.merge(rest_stops[["rest_stop_id", "highway_route"]], on="rest_stop_id")
            avg_by_route = avg_by_route.groupby(["highway_route", "food_category"], as_index=False)["price_krw"].mean()
            fig = px.bar(
                avg_by_route,
                x="highway_route",
                y="price_krw",
                color="food_category",
                barmode="group",
                title="Average Menu Price by Route and Category",
                labels={"price_krw": "Average Price (KRW)", "highway_route": "Highway Route", "food_category": "Food Category"},
            )
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

    with data_tab:
        st.markdown("### Rest Stops")
        rest_show = filtered.rename(
            columns={
                "display_name": "Rest Stop",
                "direction": "Direction",
                "highway_route": "Highway Route",
                "region": "Region",
                "traffic_group": "Traffic Group",
                "general_hours": "General Hours",
            }
        )
        st.dataframe(rest_show[["Rest Stop", "Direction", "Highway Route", "Region", "Traffic Group", "General Hours"]], use_container_width=True, hide_index=True)
        st.markdown("### Menus")
        merged = visible_menus.merge(rest_stops[["rest_stop_id", "display_name", "highway_route", "direction", "region"]], on="rest_stop_id", how="left")
        merged["Price"] = merged["price_krw"].apply(format_krw)
        merged_show = merged.rename(
            columns={
                "display_name": "Rest Stop",
                "highway_route": "Highway Route",
                "direction": "Direction",
                "region": "Region",
                "food_area": "Food Area / Store",
                "menu_item": "Menu Item",
                "food_category": "Food Category",
                "availability": "Available Time",
                "is_signature": "Signature Food",
                "recommended": "Recommended",
                "sample_rating": "Sample Rating",
                "menu_description": "Menu Description",
            }
        )
        st.dataframe(
            merged_show[["Rest Stop", "Direction", "Highway Route", "Region", "Food Area / Store", "Menu Item", "Food Category", "Price", "Available Time", "Signature Food", "Recommended", "Sample Rating", "Menu Description"]],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("### Food Areas")
        store_visible = visible_stores.rename(columns={"food_area": "Food Area / Store", "store_type": "Restaurant Type", "description": "What You Can Find", "operating_hours": "Opening Hours"})
        st.dataframe(store_visible[["rest_stop_id", "Food Area / Store", "Restaurant Type", "What You Can Find", "Opening Hours"]], use_container_width=True, hide_index=True)

    with source_tab:
        st.markdown(
            """
            ### Data note
            This project uses a runnable seed dataset for dashboard prototyping.  
            For production use, replace the CSV files in `/data` with official public-data exports.

            ### Files to replace later
            - `data/rest_stops.csv`
            - `data/menu_items.csv`
            - `data/stores.csv`

            ### Design decision in this version
            Phone numbers were removed because inaccurate contact data makes the dashboard feel unreliable.  
            Rest stop names and menu names are written in Korean, while table headers remain presentation-friendly English.
            """
        )


if __name__ == "__main__":
    render_dashboard()
