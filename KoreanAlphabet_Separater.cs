﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace YourNameSpace
{
    /// <summary>
    /// 한글 자소 분리
    /// </summary>
    class KoreanAlphabet_Separater    
    {
        //.net에서 string형은 유니코드형식
        //모든데이터가 unicode로 되어있다고 가정하고 시작한다.
        //입력데이터가 유니코드가아닐경우 string.format로 유니코드로 변환해주어야한다.
        public static string seperate(string data)
        {
            int a, b, c;//자소버퍼 초성중성종성순
            string result = "";//분리결과가 저장되는 문자열
            int cnt;

            //한글의 유니코드

            // ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ
            int[] ChoSung ={ 0x3131, 0x3132, 0x3134, 0x3137, 0x3138, 0x3139, 0x3141
            , 0x3142, 0x3143, 0x3145, 0x3146, 0x3147, 0x3148, 0x3149, 0x314a
            , 0x314b, 0x314c, 0x314d, 0x314e };

            // ㅏ ㅐ ㅑ ㅒ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅝ ㅞ ㅟ ㅠ ㅡ ㅢ ㅣ
            int[] JwungSung = {   0x314f, 0x3150, 0x3151, 0x3152, 0x3153, 0x3154, 0x3155
            , 0x3156, 0x3157, 0x3158, 0x3159, 0x315a, 0x315b, 0x315c, 0x315d, 0x315e
            , 0x315f, 0x3160, 0x3161, 0x3162, 0x3163 };

            // ㄱ ㄲ ㄳ ㄴ ㄵ ㄶ ㄷ ㄹ ㄺ ㄻ ㄼ ㄽ ㄾ ㄿ ㅀ ㅁ ㅂ ㅄ ㅅ ㅆ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ
            int[] JongSung = { 0, 0x3131, 0x3132, 0x3133, 0x3134, 0x3135, 0x3136
            , 0x3137, 0x3139, 0x313a, 0x313b, 0x313c, 0x313d, 0x313e, 0x313f
            , 0x3140, 0x3141, 0x3142, 0x3144, 0x3145, 0x3146, 0x3147, 0x3148
            , 0x314a, 0x314b, 0x314c, 0x314d, 0x314e };


            int x;
            for (cnt = 0; cnt < data.Length; cnt++)
            {
                x = (int)data[cnt];
                //한글일 경우만 분리 시행
                if (x >= 0xAC00 && x <= 0xD7A3)
                {
                    c = x - 0xAC00;
                    a = c / (21 * 28);
                    c = c % (21 * 28);
                    b = c / 28;
                    c = c % 28;
                    /*
                    a = (int)a;
                    b = (int)b;
                    c = (int)c;
                    */
                    result += string.Format("{0}{1}", (char)ChoSung[a], (char)JwungSung[b]);
                    // $c가 0이면, 즉 받침이 있을경우
                    if (c != 0)
                        result += string.Format("{0}", (char)JongSung[c]);
                }
                else
                {
                    result += string.Format("{0}", (char)x);
                }
            }
            return result;
        }
    }

    /// <summary>
    /// 조사 작성기
    /// </summary>
    public class KoreanPostpositions_Builder
    {
        public KoreanPostpositions_Builder()
        {
        }

        static string Replace(string strText)
        {
            string str = "";
            MatchCollection mc = Regex.Matches(strText, @"[가-힗]");
            foreach (Match m in mc)
            {
                str += m.Value;
            }
            return str;
        }

        /// <summary>
        /// 이/가 구분
        /// </summary>
        /// <param name="a_strSubstantive"></param>
        /// <returns></returns>
        public static string Get_이가(string a_strSubstantive)
        {
            string strRet = a_strSubstantive;

            strRet += KoreanAlphabet_Separater.seperate(strRet.Substring(strRet.Length - 1)).Length == 3 ? "이" : "가";

            return strRet;
        }

        /// <summary>
        /// 을/를 구분
        /// </summary>
        /// <param name="a_strSubstantive"></param>
        /// <returns></returns>
        public static string Get_을를(string a_strSubstantive)
        {
            string strRet = a_strSubstantive;
            
            strRet += KoreanAlphabet_Separater.seperate(strRet.Substring(strRet.Length - 1)).Length == 3 ? "을" : "를";

            return strRet;
        }

        /// <summary>
        /// 은/는 구분
        /// </summary>
        /// <param name="a_strSubstantive"></param>
        /// <returns></returns>
        public static string Get_은는(string a_strSubstantive)
        {
            string strRet = a_strSubstantive;

            strRet += KoreanAlphabet_Separater.seperate(strRet.Substring(strRet.Length - 1)).Length == 3 ? "은" : "는";

            return strRet;
        }

        /// <summary>
        /// 으로/로 구분
        /// </summary>
        /// <param name="a_strSubstantive"></param>
        /// <returns></returns>
        public static string Get_으로(string a_strSubstantive)
        {
            string strRet = a_strSubstantive;
            string strTemp = KoreanAlphabet_Separater.seperate(strRet.Substring(strRet.Length - 1));
            strRet += strTemp.Length == 3 ?
                (strTemp.Substring(2) != "ㄹ" ? "으로" : "로") : "로";

            return strRet;
        }

        /// <summary>
        /// 와/과 구분
        /// </summary>
        /// <param name="a_strSubstantive"></param>
        /// <returns></returns>
        public static string Get_와과(string a_strSubstantive)
        {
            string strRet = a_strSubstantive;

            strRet += KoreanAlphabet_Separater.seperate(strRet.Substring(strRet.Length - 1)).Length == 3 ? "과" : "와";

            return strRet;
        }

        /// <summary>
        /// 아/야 구분
        /// </summary>
        /// <param name="a_strSubstantive"></param>
        /// <returns></returns>
        public static string Get_아야(string a_strSubstantive)
        {
            string strRet = a_strSubstantive;

            strRet += KoreanAlphabet_Separater.seperate(strRet.Substring(strRet.Length - 1)).Length == 3 ? "아" : "야";

            return strRet;
        }

        /// <summary>
        /// 이라/라 구분
        /// </summary>
        /// <param name="a_strSubstantive"></param>
        /// <returns></returns>
        public static string Get_이라라(string a_strSubstantive)
        {
            string strRet = a_strSubstantive;

            strRet += KoreanAlphabet_Separater.seperate(strRet.Substring(strRet.Length - 1)).Length == 3 ? "이라" : "라";

            return strRet;
        }
    }
}
