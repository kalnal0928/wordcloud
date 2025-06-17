from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
import re
from collections import Counter
import pandas as pd

plt.rcParams['font.family'] = 'Malgun Gothic'  # 'famlily' -> 'family', 공백 제거
plt.rcParams['axes.unicode_minus'] = False


def make_wordcloud(text):
    print("텍스트 분석 시작")

    # 한국어 형태소 분석
    okt = Okt()  # 공백 제거
    clean_text = re.sub(r'[^가-힣\s]', '', text)  # '가 -힣' -> '가-힣'
    words = okt.nouns(clean_text)

    # 필터링 (2글자 이상, 불용어 제거)
    stop_words = ['의', '가', '이', '은', '는', '을', '를', '에', '와', '과', '한', '하다', '있다', '되다', '그', '저', '것', '수', '들', '지', '고', '되다', '다', '로', '으로', '에서', '에게', '한테', '께서']
    good_words = [word for word in words if len(word) >= 2 and word not in stop_words]
    
    print(f"추출된 단어: {len(good_words)}개")
    
    # 단어 빈도수 계산
    word_counts = Counter(good_words)
    df_counts = pd.DataFrame(word_counts.items(), columns=['단어', '빈도수'])
    df_counts = df_counts.sort_values(by="빈도수", ascending=False).reset_index(drop=True)
    
    print("\n단어 빈도수 상위 10개")
    print(df_counts.head(10))
    
    # 워드클라우드 생성
    wordcloud = WordCloud(
        font_path='malgun.ttf',
        width=1000,
        height=600,
        background_color='white',
        max_words=100,
        colormap='Set3').generate_from_frequencies(word_counts)
    
    # 출력
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')  # 'interpolatiion' -> 'interpolation'
    plt.axis('off')
    plt.title('워드클라우드', fontsize=20, pad=20)  # 제목
    
    plt.show()
    
    print("워드 클라우드 완성!")
    
    return wordcloud, df_counts

def read_text_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()

        print(f"{filename}에서 텍스트를 성공적으로 읽었습니다.")
        return text

    except FileNotFoundError:
        print(f"파일 {filename}을(를) 찾을 수 없습니다.")
        print("현재 폴더에 파일이 있는지 확인해주세요.")
        
    except Exception as e:
        print(f"파일 {filename} 파일을 읽는 중 오류가 발생했습니다: {e}")
        return None


if __name__ == "__main__":
    print("텍스트 파일 워드 클라우드 생성기")
    
    print("="*50)
    
    filename = "C:/AutoCoder/wordcloud.txt"  # 끝의 공백 제거
    text_content = read_text_file(filename)
    
    if text_content:
        print(f"파일 내용 길이: {len(text_content)}자")
        _, df = make_wordcloud(text_content)
        
    else:
        print("텍스트 파일을 읽는 데 실패했습니다.")