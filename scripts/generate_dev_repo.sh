#!/bin/bash

# Parent repository 이름을 묻기
echo "Enter the parent repository name:"
read parent_repo

# 새로운 repository 이름 생성
dev_repo="${parent_repo}-dev"

# GitHub CLI를 사용하여 새로운 private repository 생성
gh repo create "$dev_repo" --private --description "Development repository for $parent_repo" --gitignore Python

# 결과 확인
if [ $? -eq 0 ]; then
    echo "Successfully created repository: $dev_repo"
    
    # 새로운 repository를 현재 디렉토리에 clone
    git clone "https://github.com/crimson206/$dev_repo.git"
    
    # clone 결과 확인
    if [ $? -eq 0 ]; then
        echo "Successfully cloned repository: $dev_repo"
        
        # README 파일 생성 및 추가
        cd "$dev_repo"
        echo "# $dev_repo" > README.md
        git add README.md
        git commit -m "Add README file"
        git push origin main
        echo "Successfully added README file to repository: $dev_repo"
        
        # parent repository의 디렉토리로 이동 (상위 디렉토리로 이동)
        cd ..

    else
        echo "Failed to clone repository: $dev_repo"
    fi
else
    echo "Failed to create repository: $dev_repo"
fi
