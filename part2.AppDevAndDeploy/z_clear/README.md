# AWSweepr 완전 삭제용 
# 주의: 모든 AWS 리소스를 삭제함. 반드시 --dry-run으로 테스트 후 사용
#           i1, terraform 빼고 지워짐
#           i1은 직접 제거할 것.

# 설치
```
curl -sSfL https://raw.githubusercontent.com/jckuester/awsweeper/master/install.sh | sh
cp bin/awsweeper ~/.bin/
```

# i1와 iam terraform유저 빼고 지우기 삭제
awsweeper -dry-run  ~/Library/CloudStorage/Dropbox/Data/awsweeper/all.yml
awsweeper  ~/Library/CloudStorage/Dropbox/Data/awsweeper/all.yml

# cf) 리전 지정 삭제
awsweeper --region=eu-west-1 --force  ~/Library/CloudStorage/Dropbox/Data/awsweeper/all.yml
awsweeper --region=ap-northeast-2 --force  ~/Library/CloudStorage/Dropbox/Data/awsweeper/all.yml

# cf) 모든 리전 삭제
for region in $(aws ec2 describe-regions --query "Regions[].{Name:RegionName}" --output text); do
    awsweeper --region=$region --force  ~/Library/CloudStorage/Dropbox/Data/awsweeper/all.yml
done
