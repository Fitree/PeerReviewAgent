#!/bin/bash


Q="What is the benifit and side-effect of long term usage of melatonin?"
Q="멜라토닌을 장기간 복용할 때의 이점과 부작용을 정리해봐."
R1="R1:독성학자"
R2="R2:신경과학자"
R3="R3:내분비전문의"
R4="R4:전문약사"
R5="R5:정신과전문의"


pra-run "$Q" \
--reviewer "$R1" \
--reviewer "$R2" \
--reviewer "$R3" \
--reviewer "$R4" \
--reviewer "$R5" \
--rounds 2 \
