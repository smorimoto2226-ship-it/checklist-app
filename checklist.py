import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ==========================
# パスワード認証
# ==========================
PASSWORD = "2226"

def check_password():
    st.title("🔐 チェックリスト アクセス認証")
    pwd = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if pwd == PASSWORD:
            st.session_state["auth"] = True
            st.success("認証成功！")
        else:
            st.error("パスワードが違います")
    return st.session_state.get("auth", False)

# ==========================
# メインアプリ
# ==========================
def main_app():

    machines = [f"{i}号機" for i in range(1, 11)]
    sections = {
        "作業台": ["シャーペン", "消しゴム", "不要物"],
        "成形機": ["真鍮棒", "EJロッド", "フライパン", "不要物"]
    }

    HISTORY_FILE = "checklist_history.csv"

    # CSV読み込み（空ファイル・未作成対応）
    if os.path.exists(HISTORY_FILE):
        try:
            history_df = pd.read_csv(HISTORY_FILE)
        except pd.errors.EmptyDataError:
            history_df = pd.DataFrame()
    else:
        history_df = pd.DataFrame()

    st.title("始業前チェックリスト")
    check_data = {}

    # ----------- チェックリスト画面 ----------------
    for section, items in sections.items():
        st.subheader(section)

        # ヘッダー（項目 + 機械番号）
        header_cols = st.columns(len(machines) + 1)
        header_cols[0].markdown("**項目**")
        for i, m in enumerate(machines):
            header_cols[i + 1].markdown(f"**{m}**")

        for item in items:
            row_cols = st.columns(len(machines) + 1, gap="small")
            row_cols[0].markdown(item)
            row = {}

            for idx, machine in enumerate(machines):
                state_key = f"state_{section}_{item}_{machine}"
                btn_key = f"btn_{section}_{item}_{machine}"

                if state_key not in st.session_state:
                    st.session_state[state_key] = ""

                label = st.session_state[state_key] if st.session_state[state_key] else " "

                # ボタン幅をスマホに最適化
                if row_cols[idx + 1].button(label, key=btn_key, use_container_width=True):
                    if st.session_state[state_key] == "":
                        st.session_state[state_key] = "〇"
                    elif st.session_state[state_key] == "〇":
                        st.session_state[state_key] = "×"
                    else:
                        st.session_state[state_key] = ""

                row[machine] = st.session_state[state_key]

            # 不要物だけコメント欄（折りたたみ）
            if item == "不要物":
                comment_key = f"comment_{section}_{item}"
                with st.expander(f"{section} - {item} コメント入力"):
                    comment = st.text_input("コメントを入力", key=comment_key)
                    row["コメント"] = comment

            check_data[(section, item)] = row

    # ----------- 登録ボタン（当日上書き） ---------------
    if st.button("登録"):
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not history_df.empty and "日時" in history_df.columns:
            # 当日の履歴を削除
            history_df = history_df[~history_df["日時"].str.startswith(today)]

        new_rows = []
        for (section, item), machines_data in check_data.items():
            row = {"日時": timestamp, "セクション": section, "項目": item}
            row.update(machines_data)
            new_rows.append(row)

        new_df = pd.DataFrame(new_rows)
        history_df = pd.concat([history_df, new_df], ignore_index=True)
        history_df.to_csv(HISTORY_FILE, index=False)
        st.success("登録しました！（同日のデータを上書き）")

    # ----------- 履歴表示 ---------------
    if not history_df.empty:
        st.subheader("履歴一覧")
        st.dataframe(history_df, use_container_width=True)
        csv = history_df.to_csv(index=False).encode("utf-8")
        st.download_button("CSVダウンロード", csv, "checklist_history.csv", "text/csv")

    # ----------- 履歴削除 ---------------
    if st.button("履歴を全削除"):
        pd.DataFrame().to_csv(HISTORY_FILE, index=False)
        st.warning("履歴を削除しました")

# ==========================
# アプリ起動
# ==========================
if check_password():
    main_app()

