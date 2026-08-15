import streamlit as st
from pathlib import Path
from streamlit_extras.specialized_inputs import url_input
from core.extract_channel_info import channel_data
from core.extract_playlists import extract_playlists
from core.extract_playlist_items import extract_playlists_items
from core.extract_vid_stats import extract_vid_stats
from core.cut_off_dates import get_cutoff_date
from models.data_models import VideoAnalytics
from validation.extractor import yt_handle_extractor
from error.error_check import error_check
from reasoning.reason import get_ideas
from datetime import datetime,timezone

# Load CSS
def load_css(file_path:Path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = Path(__file__).parent / "assets/style.css"
load_css(css_path)


st.set_page_config(page_title="IdeaGen",page_icon=r'assets/writing.png')

# Session States
if 'analyzed_vids' not in st.session_state:
    st.session_state.analyzed_vids=0

if 'top_vid' not in st.session_state:
    st.session_state.top_vid=""

if 'avg_views' not in st.session_state:
    st.session_state.avg_views=0

if 'channel_url' not in st.session_state:
    st.session_state.channel_url=""

if 'yt_handle' not in st.session_state:
    st.session_state.yt_handle=""

if 'channel_info' not in st.session_state:
    st.session_state.channel_info=None

if 'playlist_data' not in st.session_state:
    st.session_state.playlist_data=[]

if 'vid_stats' not in st.session_state:
    st.session_state.vid_stats=[]

if 'merged' not in st.session_state:
    st.session_state.merged=[]

if 'ranked' not in st.session_state:
    st.session_state.ranked=[]
# Request Options

playlist_map={}

with st.container(border=True):
    st.subheader(":color[**Channel Video Idea Generator**]{foreground='#FF1F1F'}")
    new_url=url_input("Youtube Channel URL: ",placeholder="https://www.youtube.com/@yourchannel   'enter to apply'").strip()

    if new_url and new_url!=st.session_state.channel_url:
        st.session_state.channel_url=new_url

        if st.session_state.channel_url:
            st.session_state.yt_handle=yt_handle_extractor(st.session_state.channel_url)
            if st.session_state.yt_handle is not None:
                # Taking Channel Data
                channel_result=error_check(channel_data(st.session_state.yt_handle))
                st.session_state.channel_info= channel_result

                # Taking Playlist Data
            if st.session_state.channel_info is not None: 
                playlist_res=error_check(extract_playlists(st.session_state.channel_info.channel_id))
                st.session_state.playlist_data=playlist_res

    col1,col2=st.columns([1,1])
    with col1:
        ranges=["Last 30 days","Last 90 days","Last 6 Months","Last 1 Year","All Time"]
        time_frame=st.selectbox(":color[**Time Range**]{foreground='#9CFFB6'}",ranges,index=1)
    with col2:
        rankings=["Views per day","Total views","Views Per Subscriber"]
        rank_vids=st.selectbox(":color[**Rank Videos by**]{foreground='#894BDB'}",rankings,index=1)

    if isinstance(st.session_state.playlist_data,list):
        for p in st.session_state.playlist_data:
            name=p.title
            if name in playlist_map:
                name=f'{p.title} ({p.id[-6:]})'
            playlist_map[name]=p.id
        if st.session_state.channel_info is not None:
            playlist_map['All Videos (Uploads)']=st.session_state.channel_info.uploads_id
    playlists_options=list(playlist_map.keys())
    if len(playlist_map)!=0:
        playlist=st.selectbox("Select Playlist",playlists_options,index=len(playlists_options)-1)
    st.session_state.merged=[]
    if st.session_state.playlist_data:
        vids=error_check(extract_playlists_items(playlist_map[playlist]))
        if vids is not None:
            cutoff=get_cutoff_date(time_frame)

            filtered_vids=[v for v in vids if not cutoff or v.published_at>=cutoff]
            filtered_vid_ids=[v.vid_id for v in filtered_vids]

            if filtered_vid_ids:
                st.session_state.vid_stats=error_check(extract_vid_stats(filtered_vid_ids))
                if st.session_state.vid_stats:
                    stats_by_id={s.video_id:s for s in st.session_state.vid_stats}
                    for item in filtered_vids:
                        stat=stats_by_id.get(item.vid_id)
                        if stat:
                            published=datetime.strptime(item.published_at,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                            days_since=max((datetime.now(timezone.utc)-published).days,1)
                            st.session_state.merged.append(VideoAnalytics(
                                video_id=item.vid_id,
                                title=item.title,
                                published_at=item.published_at,
                                view_count=stat.view_count,
                                like_count=stat.like_count,
                                duration=stat.duration,
                                days_since=days_since,
                                views_per_day=stat.view_count/days_since,
                                views_per_sub=stat.view_count/st.session_state.channel_info.sub_count
                            ))
    
    if st.session_state.merged:
        rank_maps={
            "Views per day": lambda v: v.views_per_day,
            "Total views": lambda v: v.view_count,
            "Views Per Subscriber": lambda v: v.views_per_sub
        }

        st.session_state.ranked=sorted(st.session_state.merged,key=rank_maps[rank_vids],reverse=True)
        st.session_state.analyzed_vids=len(st.session_state.ranked)
        st.session_state.top_vid=st.session_state.ranked[0].title
        st.session_state.avg_views=f'{sum(v.view_count for v in st.session_state.ranked)/len(st.session_state.ranked):.2f}'
                 
    generate=st.button("✨ **Generate Ideas**",width='stretch',key="red_btn")

if generate:
    result=None
    
    with st.container(border=True):
        stat_cols1, stat_cols2 = st.columns([1, 4])
        with stat_cols1:
            try:
                st.image(st.session_state.channel_info.avatar_url)
            except:
                st.write("👥")
        with stat_cols2:
            st.markdown(f"### {st.session_state.channel_info.title}")
            st.caption(f"👥 {int(st.session_state.channel_info.sub_count):,} subscribers")
            desc = st.session_state.channel_info.description
            if desc:
                truncated = desc[:120] + "..." if len(desc) > 120 else desc
                st.caption(truncated)

    # Channel Metric
    metric1,metric2,metric3=st.columns(3)
    
    with metric1:
        st.metric("Videos Analyzed",icon='📄',value=st.session_state.analyzed_vids)
    with metric2:
        st.metric("Top Performer",icon='⭐',value=st.session_state.top_vid)
    with metric3:
        st.metric("Avg views/video",icon='✒️',value=st.session_state.avg_views)

    if st.session_state.ranked:
        with st.spinner("Generating Content..."):
                    scope_label = f"{time_frame} · {playlist}"
                    result=error_check(get_ideas(
                            channel_title=st.session_state.channel_info.title,
                            channel_description=st.session_state.channel_info.description,
                            sub_count=st.session_state.channel_info.sub_count,
                            scope_label=scope_label,
                            ranked_videos=st.session_state.ranked
                        ))

    if result is not None:
        st.markdown("### :color[Suggested Video Ideas]{foreground='#07F544'}")
        with st.container(border=True):
            for idea in result.ideas:
                badge_color = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}[idea.impact.value]
                st.markdown(f"**{idea.title}** {badge_color} `{idea.impact.value} impact`")
                st.write(idea.concept)
                st.caption(idea.reasoning)

        
        