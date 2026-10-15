# 🎬 Youtube Idea Generator

> **Turn your YouTube channel's performance data into data-driven video ideas.**

Channel Video Idea Generator is a Streamlit application that analyzes a YouTube channel's actual video performance and uses an LLM to generate **channel-specific video ideas**.

Instead of prompting an LLM with something generic like *"give me some YouTube video ideas"*, the application first gathers information about the channel and its videos through the **YouTube Data API**, filters and ranks the available videos based on performance, and then provides that information as context to an LLM.

The result is a set of video ideas with **concepts, data-grounded reasoning, and an estimated impact level**.

---

## ✨ Features

- 🔎 **YouTube channel analysis**

  - Extracts channel information from a YouTube channel URL
  - Retrieves subscriber count, channel description, and upload information

- 📊 **Video performance analysis**

  - Retrieves video statistics including:
    - Views
    - Likes
    - Publication date
    - Duration
  - Calculates additional performance metrics such as:
    - Views per day
    - Views per subscriber

- 📅 **Flexible analysis periods**

  - Last 30 days
  - Last 90 days
  - Last 6 months
  - Last 1 year
  - All time

- 📁 **Playlist-based analysis**

  - Analyze the entire channel's uploads
  - Or select a specific playlist to narrow the analysis scope

- 🏆 **Multiple ranking strategies**

  - Views per day
  - Total views
  - Views per subscriber

- 🧠 **LLM-powered reasoning**

  - Provides the LLM with actual channel and video performance data
  - Generates ideas based on patterns found in the channel's existing content
  - Avoids relying solely on generic YouTube advice

- 📋 **Structured AI output**

  - Every generated idea contains:
    - A specific video title
    - A concept
    - Data-grounded reasoning
    - An impact rating

- 🟢🟡🔴 **Impact scoring**

  - **HIGH** — strongly supported by patterns in proven content
  - **MEDIUM** — related to successful content but explores a different angle
  - **LOW** — fills a content gap or diversifies the channel with limited supporting evidence

- 🛡️ **API error handling**

  - Handles missing channels
  - API rate limits and quota errors
  - Forbidden/API configuration errors
  - Unexpected API failures

---

## 🧠 How It Works

The application follows a simple data → analysis → reasoning pipeline.

```text
YouTube Channel URL
        │
        ▼
Extract Channel Information
        │
        ├── Channel ID
        ├── Channel Name
        ├── Description
        ├── Subscriber Count
        └── Uploads Playlist
        │
        ▼
Retrieve Playlists
        │
        ▼
Select Playlist + Time Range
        │
        ▼
Retrieve Playlist Videos
        │
        ▼
Retrieve Video Statistics
        │
        ├── Views
        ├── Likes
        ├── Duration
        └── Publication Date
        │
        ▼
Calculate Performance Metrics
        │
        ├── Views / Day
        └── Views / Subscriber
        │
        ▼
Rank Videos
        │
        ▼
Select Top Performing Videos
        │
        ▼
Channel + Video Data → LLM
        │
        ▼
Structured Video Ideas
        │
        ├── Title
        ├── Concept
        ├── Reasoning
        └── Impact Level
```

### 1. Channel Data Extraction

The application starts with a YouTube channel URL and extracts the channel handle.

The YouTube Data API is then used to retrieve information about the channel, including its:

- Channel ID
- Uploads playlist
- Name
- Description
- Subscriber count
- Channel avatar

### 2. Video Data Collection

The selected playlist is queried to obtain the videos within the chosen time range.

The application then retrieves statistics for those videos through the YouTube Data API.

For each video, the application keeps track of metrics such as:

```text
Views
Likes
Publication date
Duration
```

It also calculates additional metrics:

```text
Views per day = Total views / Days since publication

Views per subscriber = Total views / Channel subscribers
```

These metrics provide more useful signals than simply looking at total views.

### 3. Video Ranking

The analyzed videos can be ranked using three different metrics:

| Ranking              | What it measures                                    |
| -------------------- | --------------------------------------------------- |
| Views per day        | How quickly a video is accumulating views           |
| Total views          | Overall accumulated performance                     |
| Views per subscriber | Performance relative to the channel's audience size |

The highest-ranked videos are then used as the primary performance context for the LLM.

### 4. LLM Reasoning

The application sends the LLM information about the channel together with the performance data of the top-ranked videos.

The model receives context including:

- Channel name
- Channel description
- Subscriber count
- Analysis scope
- Video titles
- View counts
- Views per day
- Like counts
- Publication age
- Video duration

This allows the model to reason about **what has actually worked for that particular channel** rather than generating disconnected ideas.

The system prompt specifically instructs the model to make every recommendation traceable to the supplied channel data.

### 5. Structured Results

The generated response is validated against a Pydantic schema.

Each idea follows the same structure:

```text
Video Idea
├── Title
├── Concept
├── Reasoning
└── Impact
```

This makes the LLM response predictable and easier for the application to render.

---

## 📊 Example of the Analysis

Suppose a channel contains several videos where a particular topic or format consistently performs better than the channel average.

Rather than simply generating another random topic, the application can provide the LLM with the relevant performance data and ask it to extend the successful pattern.

For example:

```text
"Example Video" — 42,000 views (1,400/day), 2,100 likes
"Another Video" — 31,000 views (1,033/day), 1,500 likes
"Older Video" — 8,000 views (130/day), 420 likes
```

The LLM can use these differences to determine which content patterns appear promising and explain **why** a proposed idea may have potential.

The reasoning is therefore tied to the channel's own historical performance rather than generic recommendations.

---

## 🧰 Tech Stack

### Application

- **Python**
- **Streamlit**

### Data

- **YouTube Data API v3**
- `google-api-python-client`

### AI / LLM

- **Google Gemini**
- **LangChain**
- Structured LLM output

### Data Validation

- **Pydantic**

### Configuration

- **python-dotenv**

### Package Management

- **uv**

---

## 📁 Project Structure

```text
YT-Idea-Gen/
│
├── assets/
│   ├── style.css
│   └── writing.png
│
├── core/
│   ├── cut_off_dates.py
│   ├── extract_channel_info.py
│   ├── extract_playlist_items.py
│   ├── extract_playlists.py
│   └── extract_vid_stats.py
│
├── error/
│   └── error_check.py
│
├── models/
│   └── data_models.py
│
├── reasoning/
│   ├── reason.py
│   └── sys_prompt/
│       └── sys_msg.txt
│
├── validation/
│   ├── extractor.py
│   └── validator.py
│
├── main.py
├── pyproject.toml
└── uv.lock
```

### Module Overview

| Module        | Responsibility                                           |
| ------------- | -------------------------------------------------------- |
| `core/`       | YouTube data extraction and performance calculations     |
| `models/`     | Pydantic data models and structured output schemas       |
| `reasoning/`  | LLM initialization, prompt handling, and idea generation |
| `validation/` | YouTube URL validation and handle extraction             |
| `error/`      | API error handling and user-facing error messages        |
| `assets/`     | Application assets and styling                           |
| `main.py`     | Streamlit application and overall workflow               |

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

- Python **3.13+**
- A YouTube Data API v3 API key
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd YT-Idea-Gen
```

### 2. Install dependencies

This project uses **uv** for dependency management.

```bash
uv sync
```

Alternatively, install the dependencies using pip:

```bash
pip install -e .
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
YT_DATA_API=your_youtube_data_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
```

Never commit your `.env` file or expose your API keys publicly.

### 4. Run the application

```bash
streamlit run main.py
```

The application will open in your browser.

---

## 🖥️ Usage

1. Enter a YouTube channel URL.
2. Select the desired **time range**.
3. Choose how videos should be ranked.
4. Select either the channel's uploads or a specific playlist.
5. Click **Generate Ideas**.
6. The application analyzes the selected videos.
7. The LLM receives the channel and performance context.
8. Review the generated video ideas and their impact levels.

---

## 🛡️ Error Handling

The application includes explicit handling for common YouTube API failures.

| Error                       | Application Response                 |
| --------------------------- | ------------------------------------ |
| Channel not found           | Prompts the user to check the URL    |
| Rate limit / quota exceeded | Informs the user to try again later  |
| Forbidden request           | Indicates an API configuration issue |
| Unknown API error           | Displays a generic failure message   |

API responses are converted into a common `ChannelFetchError` enum so that the UI can handle different failure conditions consistently.

---

## 🎯 Design Philosophy

The core idea behind this project is simple:

> **An LLM can generate ideas, but giving it the right context makes those ideas significantly more useful.**

A generic prompt can produce an endless number of plausible YouTube ideas. The harder problem is determining **which ideas make sense for a specific creator**.

This project therefore focuses on building the context first:

**Channel → Content → Performance → Patterns → Ideas**

The LLM is used as the reasoning layer on top of that data rather than as the source of the data itself.

---

## 🔮 Future Improvements

Some potential directions for expanding the project include:

- Incorporating additional engagement metrics
- Comparing performance across different content formats
- Adding thumbnail/title pattern analysis
- Tracking generated ideas against their eventual performance
- Maintaining historical channel snapshots
- Adding more ranking and filtering strategies
- Supporting additional LLM providers
- Allowing creators to compare multiple playlists or content categories

---

## ⚠️ Limitations

The generated impact level is an **AI-assisted estimate**, not a guarantee of future performance.

The quality of recommendations also depends on the amount and quality of historical channel data available. A channel with very little content or highly inconsistent performance provides less evidence for reliable pattern detection.

The application also depends on access to the YouTube Data API and the associated API quota.

---

## 📜 License

This project is available under the license included in this repository.

---

## 👨‍💻 Author

**KaisoX24**

Built as an experiment in combining **YouTube analytics, structured data extraction, and LLM reasoning** to make content planning more data-driven.
