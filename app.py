import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import emoji
import re
from collections import Counter
from wordcloud import WordCloud

# Configure page
st.set_page_config(page_title="📊 WhatsApp Chat Analyzer", layout="wide")
st.title("📊 WhatsApp Chat Analyzer with Tabs")

# Upload
uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type=["txt"])

def parse_chat(text_data):
    # Updated regex for DD/MM/YY and optional colon after sender
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s([^:]+)(?::\s)?(.*)$'
    messages = []
    for line in text_data.split("\n"):
        match = re.match(pattern, line)
        if match:
            date, time, sender, message = match.groups()
            # Filter system messages
            system_keywords = ["added", "created", "left", "changed"]
            if any(k in sender.lower() for k in system_keywords):
                continue
            if message.strip() == "":
                continue
            messages.append([date, time, sender.strip(), message.strip()])
    df = pd.DataFrame(messages, columns=["Date", "Time", "Sender", "Message"])
    return df

if uploaded_file is not None:
    text_data = uploaded_file.read().decode("utf-8")
    df = parse_chat(text_data)

    if df.empty:
        st.error("No valid chat messages found after parsing. Please check your chat file format.")
    else:
        # Convert date & datetime
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        df["DateTime"] = pd.to_datetime(df["Date"].dt.strftime("%Y-%m-%d") + " " + df["Time"], errors="coerce")
        df.dropna(subset=["DateTime"], inplace=True)

        # Sidebar user filter including Overall
        users = ["Overall"] + sorted(df["Sender"].unique().tolist())
        selected_user = st.sidebar.selectbox("Select User", users)
        if selected_user != "Overall":
            df_filtered = df[df["Sender"] == selected_user]
        else:
            df_filtered = df.copy()

        # Set plot style and size defaults
        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = (8, 4)
        plt.rcParams['font.size'] = 12

        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Stats",
            "📅 Messages Over Time",
            "😂 Emojis",
            "📷 Media Shares",
            "☁️ Word Cloud",
            "📊 Active Days / Months"
        ])

        # Tab 1: Basic Stats
        with tab1:
            st.subheader("Basic Statistics")
            st.write(f"**Total messages:** {len(df_filtered)}")
            if selected_user == "Overall":
                st.write(f"**Total users:** {df['Sender'].nunique()}")
                st.write(f"**Users:** {', '.join(df['Sender'].unique())}")
                st.subheader("Messages per User")
                user_counts = df["Sender"].value_counts()
                fig, ax = plt.subplots()
                user_counts.plot(kind="bar", color="skyblue", ax=ax)
                plt.xticks(rotation=45)
                plt.xlabel("User")
                plt.ylabel("Messages")
                st.pyplot(fig)

        # Tab 2: Messages Over Time
        with tab2:
            st.subheader("Messages Over Time")
            if df_filtered["DateTime"].isnull().all():
                st.warning("No valid dates found for plotting.")
            else:
                daily_counts = df_filtered.groupby(df_filtered["DateTime"].dt.date).size()
                fig, ax = plt.subplots()
                daily_counts.plot(kind="line", marker="o", color="purple", ax=ax)
                plt.title("Messages Over Time (Daily)")
                plt.xlabel("Date")
                plt.ylabel("Number of Messages")
                st.pyplot(fig)

                monthly_counts = df_filtered.groupby(df_filtered["DateTime"].dt.to_period("M")).size()
                fig2, ax2 = plt.subplots()
                monthly_counts.plot(kind="line", marker="o", color="green", ax=ax2)
                plt.title("Messages Over Time (Monthly)")
                plt.xlabel("Month")
                plt.ylabel("Number of Messages")
                st.pyplot(fig2)

                st.subheader("Messages by Hour of Day")
                df_filtered["Hour"] = df_filtered["DateTime"].dt.hour
                hour_counts = df_filtered.groupby("Hour").size()
                fig3, ax3 = plt.subplots()
                hour_counts.plot(kind="bar", color="orange", ax=ax3)
                plt.xlabel("Hour of Day")
                plt.ylabel("Number of Messages")
                plt.xticks(rotation=0)
                st.pyplot(fig3)

        # Tab 3: Emoji Analysis
        with tab3:
            st.subheader("Top Emojis Used")
            emoji_ctr = Counter()
            emojis_list = list(emoji.EMOJI_DATA.keys())
            emoji_pattern = re.compile('|'.join(re.escape(e) for e in emojis_list))

            for _, row in df_filtered.iterrows():
                found_emojis = emoji_pattern.findall(row["Message"])
                for emj in found_emojis:
                    emoji_ctr[emj] += 1

            top10emojis = pd.DataFrame(columns=['emoji', 'emoji_count', 'emoji_description'])
            for i, (emj, count) in enumerate(emoji_ctr.most_common(10)):
                desc = emoji.demojize(emj)[1:-1]  # remove colons
                top10emojis.loc[i] = [emj, count, desc]

            if top10emojis.empty:
                st.write("No emojis found in messages.")
            else:
                st.subheader("Emoji Usage Table (Descriptions Only)")
                st.dataframe(top10emojis[['emoji_description', 'emoji_count']])

                st.subheader("Emoji Usage Graph (Real Emojis)")
                fig, ax = plt.subplots()
                sns.barplot(x='emoji_count', y='emoji', data=top10emojis, palette="Paired_r", ax=ax)
                ax.set_xlabel("Count")
                ax.set_ylabel("Emoji")
                ax.set_title("Top 10 Emojis Used")
                st.pyplot(fig)

        # Tab 4: Media Shares
        with tab4:
            st.subheader("Top Media Senders")
            media_df = df_filtered[df_filtered["Message"] == "<Media omitted>"]
            if media_df.empty:
                st.write("No media messages found.")
            else:
                top_media = media_df["Sender"].value_counts().head(10)
                fig, ax = plt.subplots()
                top_media.plot(kind="bar", color="green", ax=ax)
                plt.xticks(rotation=45)
                plt.xlabel("User")
                plt.ylabel("Media Shared")
                plt.title("Top 10 Media Senders")
                st.pyplot(fig)

        # Tab 5: Word Cloud
        with tab5:
            st.subheader("Word Cloud")
            text = " ".join(df_filtered["Message"].dropna())
            if len(text.strip()) == 0:
                st.write("No text messages found for word cloud.")
            else:
                wc = WordCloud(width=800, height=400, background_color="white").generate(text)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)

        # Tab 6: Active Days / Months
        with tab6:
            st.subheader("Active Days and Months")
            df_filtered["Weekday"] = df_filtered["DateTime"].dt.day_name()
            weekday_counts = df_filtered["Weekday"].value_counts().reindex(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            )
            fig, ax = plt.subplots()
            sns.barplot(x=weekday_counts.index, y=weekday_counts.values, palette="pastel", ax=ax)
            ax.set_title("Messages by Day of Week")
            ax.set_xlabel("Day")
            ax.set_ylabel("Message Count")
            plt.xticks(rotation=45)
            st.pyplot(fig)

            df_filtered["Month_Year"] = df_filtered["DateTime"].dt.to_period("M").astype(str)
            month_counts = df_filtered["Month_Year"].value_counts().sort_index()
            fig2, ax2 = plt.subplots()
            month_counts.plot(kind="bar", color="coral", ax=ax2)
            ax2.set_title("Messages by Month-Year")
            ax2.set_xlabel("Month-Year")
            ax2.set_ylabel("Message Count")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

else:
    st.info("Please upload a WhatsApp chat file to start analysis.")
