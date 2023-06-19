# Design_Pattern_Term_Project
Main.exe 실행<br>
시뮬레이터 명령어
1. l XXXX.bin => Load Program 프로그램 로드<br>
   ex) l as_ex01_arith.bin
   
2. j 0xXXXXXX => jump to 0xXXXXXX PC값을 변경<br>
   ex) j 0x00400004
   
3. g => go program 프로그램 전체 실행<br>

4. s => step 프로그램 한 스텝씩 실행<br>

5. m 0xXXXXXX 0xXXXXXX => 메모리 0xXXXXXX 부터 0xXXXXXX까지 내용 출력<br>
   ex) m 0x10000000 0x10000010
   
6. r => Register 현 상태 출력<br>

7. x => 시뮬레이터 종료<br>

8. sr $XX value => Register XX의 값을 value로 교체<br>
   ex) sr $15 0x12345678
   
9. sm 0xXXXXXX value => 메모리 0xXXXXXX 위치의 값을 value로 교체<br>
   ex) sm 0x1000000C 0xABCDEF00
