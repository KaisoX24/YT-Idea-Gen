from models.data_models import ChanneInfo,PlaylistInfo,ChannelFetchError
import streamlit as st

def error_check(result:ChanneInfo|PlaylistInfo|ChannelFetchError):
    if isinstance(result, ChannelFetchError):
        match result:
            case ChannelFetchError.NOT_FOUND:
                st.error("Couldn't find that channel. Check the URL and try again.")
            case ChannelFetchError.RATE_LIMITED:
                st.error("Too many requests right now. Try again in a minute.")
            case ChannelFetchError.FORBIDDEN:
                st.error("Something's wrong with the API setup. Check your API key.")
            case ChannelFetchError.UNKNOWN:
                st.error("Something went wrong. Try again.")
    else:
        return result
        