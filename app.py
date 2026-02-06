import streamlit as st
import pandas as pd
import os
import sys
import time
import json

# Ensure we can import from tools
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
try:
    from scrape_leads import scrape_profile, OUTPUT_FILE
except ImportError:
    st.error("Could not import scraper tool. Make sure 'tools/scrape_leads.py' exists.")
    st.stop()

st.set_page_config(
    page_title="Lead Scraper Pro",
    page_icon="🦷",
    layout="wide"
)

# Custom CSS for a professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #0A66C2; /* LinkedIn Blue */
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
    }
    .stButton>button {
        background-color: #0A66C2;
        color: white;
        border-radius: 5px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists(OUTPUT_FILE):
        return pd.read_csv(OUTPUT_FILE)
    return pd.DataFrame(columns=['Name', 'Title', 'Company', 'Email', 'Valid_Syntax'])

def main():
    st.markdown('<p class="main-header">Lead Scraper Pro 🚀</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Extract and Enrich LinkedIn Profiles</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("Configuration")
        cookie = st.text_input("LinkedIn 'li_at' Cookie", type="password", help="Required for live scraping. Leave empty for Demo Mode.")
        demo_mode = st.checkbox("Force Demo Mode", value=False, help="Simulate extraction without network requests.")
        
        st.info("💡 **Tip**: Use Demo Mode to test the UI logic without needing a valid cookie.")
        st.markdown("---")
        st.markdown("### Status")
        if cookie:
            st.success("Cookie Loaded")
        else:
            st.warning("No Cookie (Demo Mode)")



    # Data Display
    st.subheader("Workspace")
    
    tab_search, tab_extract, tab_analytics = st.tabs(["🔍 Discovery (Search)", "⬇️ Extraction", "📊 Analytics"])

    # --- TAB 1: SEARCH ---
    with tab_search:
        st.markdown("### Find LinkedIn Profiles")
        
        col_search, col_api = st.columns([3, 1])
        with col_search:
             search_query = st.text_input("Search Query", placeholder='e.g. "site:linkedin.com/in/ dentist New York"')
        with col_api:
             api_key = st.text_input("Serper API Key (Optional)", type="password", help="Get free key at serper.dev for 100% reliability.")
             
        num_results = st.slider("Max Results", 5, 50, 10)
        
        if st.button("Search on Google 🔎"):
            if not search_query:
                st.warning("Please enter a query.")
            else:
                # Auto-append site filter if not present
                final_query = search_query
                if "site:" not in search_query:
                    final_query = f'site:linkedin.com/in/ {search_query}'
                
                valid_urls = []
                
                # STRATEGY 1: PROFESSIONAL API (If Key provided)
                if api_key:
                    try:
                        import requests
                        st.info(f"Using Serper.dev API for: '{final_query}'...")
                        
                        endpoint = "https://google.serper.dev/search"
                        payload = json.dumps({"q": final_query, "num": num_results})
                        headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
                        
                        response = requests.post(endpoint, headers=headers, data=payload)
                        data = response.json()
                        
                        if 'organic' in data:
                            for result in data['organic']:
                                url = result.get('link', '')
                                if "linkedin.com/in/" in url:
                                    valid_urls.append(url)
                        else:
                            st.error(f"API Error: {data}")
                            
                    except Exception as e:
                         st.error(f"API Request Failed: {e}")

                # STRATEGY 2: FREE SCRAPING (DuckDuckGo)
                else:
                    try:
                        from duckduckgo_search import DDGS
                        st.info(f"Using Free Search (DDG) for: '{final_query}'...")
                        
                        # DuckDuckGo Search
                        results = DDGS().text(final_query, max_results=num_results)
                        
                        # Debug: Show how many raw results came back
                        # st.toast(f"DDG Raw Results: {len(results) if results else 0}")
                        
                        if results:
                            for r in results:
                                url = r.get('href', '')
                                # Relaxed filter
                                if "linkedin.com" in url:
                                    valid_urls.append(url)
                            
                        # Fallback: If strict filter failed, show all URLS (debug)
                        if not valid_urls and results:
                             # st.warning("Found results but they didn't match 'linkedin.com'.")
                             pass
                            
                    except ImportError:
                        st.error("Library 'duckduckgo-search' not installed. Please run `run_ui.bat` again.")
                    except Exception as e:
                        st.error(f"Search failed: {e}")

                # RESULT PROCESSING
                # Deduplicate
                valid_urls = list(dict.fromkeys(valid_urls))
                
                if valid_urls:
                    st.success(f"Found {len(valid_urls)} profiles!")
                    st.code("\n".join(valid_urls))
                    
                    if st.button("Copy to Extraction Tab"):
                         pass 
                    
                    st.session_state['found_urls'] = "\n".join(valid_urls)
                    st.success("URLs saved to memory! Go to 'Extraction' tab to use them.")
                    
                else:
                    st.warning("⚠️ Live Search yielded 0 results. Switching to DEMO MOCK DATA.")
                    
                    mock_urls = [
                        "https://www.linkedin.com/in/demo-user-1",
                        "https://www.linkedin.com/in/demo-architect-madrid",
                        "https://www.linkedin.com/in/demo-ceo-realestate",
                        "https://www.linkedin.com/in/demo-founder-startup"
                    ]
                    
                    st.code("\n".join(mock_urls))
                    st.session_state['found_urls'] = "\n".join(mock_urls)
                    st.info("✅ Mock URLs loaded.")

    # --- TAB 2: EXTRACTION ---
    with tab_extract:
        st.markdown("### Extract Data")
        
        # Check if we have urls from search
        default_urls = ""
        if 'found_urls' in st.session_state:
            default_urls = st.session_state['found_urls']
            st.info("Loaded URLs from Search tab.")

        urls_input = st.text_area("Target Profile URLs (one per line)", value=default_urls, height=150, placeholder="https://www.linkedin.com/in/example-one\nhttps://www.linkedin.com/in/example-two")
        
        start_btn = st.button("Start Extraction ⚡")

        if start_btn:
            urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
            
            if not urls:
                st.warning("Please enter at least one URL.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                st.subheader("Processing Logs")
                log_container = st.container()
                
                for i, url in enumerate(urls):
                    status_text.text(f"Scraping {url}...")
                    with log_container:
                        st.text(f"[{time.strftime('%H:%M:%S')}] Requesting: {url}")
                    
                    try:
                        scrape_profile(url, cookie=cookie if cookie else None, demo_mode=demo_mode)
                        st.success(f"✅ Finished: {url}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                    
                    progress_bar.progress((i + 1) / len(urls))
                    time.sleep(1) 
                
                status_text.text("Extraction Complete!")
                st.balloons()
                # Refresh data
                st.rerun()

    # --- TAB 3: ANALYTICS ---
    with tab_analytics:
        df = load_data()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Download Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV 📥",
                data=csv,
                file_name='leads_export.csv',
                mime='text/csv',
            )
            
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Leads", len(df))
            with col_b:
                valid_emails = df['Valid_Syntax'].sum() if 'Valid_Syntax' in df.columns else 0
                st.metric("Valid Emails", f"{valid_emails} ({valid_emails/len(df):.0%})")
            
            if 'Company' in df.columns:
                st.caption("Companies")
                st.bar_chart(df['Company'].value_counts())
        else:
            st.info("No extracted data available yet.")


if __name__ == "__main__":
    main()
