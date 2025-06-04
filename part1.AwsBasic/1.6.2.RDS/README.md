# Info
* RDS 구현 예(Mysql 사용)
* PowerUser가 아닐 경우 IAM에서 AmazonRDSFullAccess,WorkLinkServiceRolePolicy 줄 것.

# 실행 절차
1. 폴더로 이동
```
cd
cd aws/part1.AwsBasic/1.6.2.RDS
```

2. init 및 apply
* 생성 6분,삭제 8분 정도 걸림[Snapshot생성]
* * 주의
  - password는 DB의 비번인데 8자이상이며 대문자와 숫자 포함해야 함.
  - terraform Apply 시 Parameter groups 혹은 Option Group 삭제 Error시 Aws Console의 RDS Service에서 제거
  - Parameter groups 혹은 Option Group 삭제 Error시 Aws Service RDS UI에서 Snapshots 제거
  - 삭제시 시간 갭이 있음. 빨리 하고 싶으면 다른 Region에서 실행 할 것.

```
terraform init
terraform apply -auto-approve  -var password=Nowage12kitri
```


3. Instance 생성 확인
* AWS Console → RDS
```
#sudo apt-get install -y mysql-client

cat terraform.tfstate |grep endpoint
mysql -uroot -h <url> -pNowage12kitri
  show databases;
  exit
```

* cf) Mysql Exmaple
```
show databases
use mydb
create table mytable(id int primary key,name varchar(20));
show tables;
insert into mytable values(1,'aa');
select * from mytable;
drop table mytable;
show tables;
```

4. destroy
```
terraform destroy -auto-approve -var password=Nowage12kitri
```






# Info about Terraform AWS RDS Example

This folder contains a simple Terraform module that deploys a database instance (MySQL by default) in [AWS](https://aws.amazon.com/)
to demonstrate how you can use Terratest to write automated tests for your AWS Terraform code. This module deploys an [RDS
Instance](https://aws.amazon.com/rds/) and associates it with an option group and parameter group to customize it.

Check out [test/terraform_aws_rds_example_test.go](/test/terraform_aws_rds_example_test.go) to see how you can write
automated tests for this module and validate the configuration of the parameters and options.

This module does not use the database instance created in any way. It can be used though to validate any combination of inputs
passed while creating database instances in AWS RDS. Hence the plain text simple password used here should not have any security
implications.

**WARNING**: This module and the automated tests for it deploy real resources into your AWS account which can cost you
money. The resources are all part of the [AWS Free Tier](https://aws.amazon.com/rds/free/), so if you haven't used that up,
it should be free, but you are completely responsible for all AWS charges.
