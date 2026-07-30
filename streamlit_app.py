import os
import tempfile
import streamlit as st
from yt_dlp import YoutubeDL

# 페이지 기본 설정
st.set_page_config(
    page_title="유튜브 MP3 변환기", page_icon="🎵", layout="centered"
)

st.title("🎵 유튜브 to MP3 다운로더")
st.write("유튜브 링크를 입력하면 MP3 음원 파일로 변환해 드립니다.")

# 사용자 링크 입력
url = st.text_input("유튜브 영상 링크를 입력하세요:")

if st.button("MP3 변환 및 다운로드 준비"):
  if not url:
    st.warning("유튜브 링크를 먼저 입력해주세요.")
  else:
    # 임시 디렉토리를 만들어 파일 저장 후 처리
    with tempfile.TemporaryDirectory() as temp_dir:
      ydl_opts = {
          # 포맷 오류(Requested format is not available)를 막기 위해 가장 범용적인 설정으로 변경
          "format": "best/bestaudio",
          "postprocessors": [
              {
                  "key": "FFmpegExtractAudio",
                  "preferredcodec": "mp3",
                  "preferredquality": "192",
              }
          ],
          # 임시 폴더 경로에 파일 이름 지정
          "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
          "restrictfilenames": True,  # 파일 이름에 특수문자 제거
          # 유튜브 차단 우회 및 안정성 향상을 위한 클라이언트 설정
          "extractor_args": {"youtube": {"player_client": ["web", "mweb"]}},
      }

      try:
        with st.spinner(
            "변환 중입니다... 잠시만 기다려 주세요! (영상의 길이에 따라 시간이"
            " 걸릴 수 있습니다)"
        ):
          with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            # 변환된 파일명 찾기
            audio_filename = f"{ydl.prepare_filename(info_dict)}"
            # 확장자를 mp3로 변경
            base, _ = os.path.splitext(audio_filename)
            mp3_filename = base + ".mp3"

        st.success("변환이 완료되었습니다!")

        # 파일 읽어서 다운로드 버튼 제공
        if os.path.exists(mp3_filename):
          with open(mp3_filename, "rb") as f:
            audio_bytes = f.read()

          # 웹에서 바로 들을 수 있는 오디오 플레이어
          st.audio(audio_bytes, format="audio/mp3")

          # 다운로드 버튼
          st.download_button(
              label="📥 MP3 파일 다운로드",
              data=audio_bytes,
              file_name=os.path.basename(mp3_filename),
              mime="audio/mp3",
          )
        else:
          st.error("파일 변환 중 오류가 발생했습니다.")

      except Exception as e:
        st.error(
            f"에러가 발생했습니다: {e}\n\n(참고: 유튜브 측의 보안 정책이나"
            " 클라우드 서버 IP 차단으로 인해 발생할 수 있습니다.)"
        )
