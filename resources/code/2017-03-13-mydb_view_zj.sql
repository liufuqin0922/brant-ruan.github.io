/* 2017-03-09 */
use yzmon;

/* ------------------------- 1 ------------------------- */
drop view if exists view_inner_zj_bid2num_0;
create view view_inner_zj_bid2num_0
as
select * from branch1;
drop view if exists view_inner_zj_bid2num_1;
create view view_inner_zj_bid2num_1
as
select branch2_branch1_id,count(branch2_branch1_id) as branch2_num from branch2 group by branch2_branch1_id;
drop view if exists view_inner_zj_bid2num;
create view view_inner_zj_bid2num
as
select branch1_id as bid1, branch1_name as name, branch2_num as bid2num 
	from view_inner_zj_bid2num_0 join view_inner_zj_bid2num_1
	on view_inner_zj_bid2num_0.branch1_id = view_inner_zj_bid2num_1.branch2_branch1_id;

/* ------------------------- 2 ------------------------- */
drop view if exists view_inner_zj_devnum_1;
create view view_inner_zj_devnum_1
as
select devorg_id,devorg_branch2_id
	from devorg;

drop view if exists view_inner_zj_devnum_2;
create view view_inner_zj_devnum_2
as
select branch2_id,branch2_branch1_id,count(devorg_id) as ter_num
	from view_inner_zj_devnum_1 join branch2
		on view_inner_zj_devnum_1.devorg_branch2_id=branch2.branch2_id
	group by branch2_id;

drop view if exists view_inner_zj_devnum_3;
create view view_inner_zj_devnum_3
as
select branch2_branch1_id,sum(ter_num) as devnum
	from view_inner_zj_devnum_2
	group by branch2_branch1_id;

drop view if exists view_inner_zj_devnum;
create view view_inner_zj_devnum
as
select branch1_id as bid1, branch1_name as name,devnum
	from view_inner_zj_devnum_3 join branch1
		on branch1.branch1_id = view_inner_zj_devnum_3.branch2_branch1_id;

/* ------------------------- 3 ------------------------- */
drop view if exists view_inner_zj_devcount_0;
create view view_inner_zj_devcount_0
as
select distinct devstate_base_devid
	from devstate_base;

drop view if exists view_inner_zj_devcount_1;
create view view_inner_zj_devcount_1
as
select devorg_branch2_id, count(devorg_id) as count_num
	from devorg join view_inner_zj_devcount_0
		on devorg.devorg_id=view_inner_zj_devcount_0.devstate_base_devid
	group by devorg_branch2_id;

drop view if exists view_inner_zj_devcount_2;
create view view_inner_zj_devcount_2
as
select branch2_branch1_id, count_num
	from branch2 join view_inner_zj_devcount_1
		on branch2.branch2_id = view_inner_zj_devcount_1.devorg_branch2_id;

/* ------------------------- 4 ------------------------- */
drop view if exists view_inner_zj_devcount;
create view view_inner_zj_devcount
as
select branch1_id as bid1, branch1_name as name, sum(count_num) as devcount
	from branch1 join view_inner_zj_devcount_2
		on branch1.branch1_id = view_inner_zj_devcount_2.branch2_branch1_id
	group by bid1;

/* view_inner_zj_devunreg */
drop view if exists view_inner_zj_devunreg_1;
create view view_inner_zj_devunreg_1
as
select devstate_base_devid,count(devstate_base_devid) as count_num
	from devstate_base
	group by devstate_base_devid;

drop view if exists view_inner_zj_devunreg_2;
create view view_inner_zj_devunreg_2
as
select left(devstate_base_devid, 4) as l4_id , count_num
	from view_inner_zj_devunreg_1
	where devstate_base_devid not in (select devorg_id from devorg);

drop view if exists view_inner_zj_devunreg_3;
create view view_inner_zj_devunreg_3
as
select branch1_id as bid1, branch1_name as name,sum(count_num) as devunreg
	from view_inner_zj_devunreg_2 join branch1
		on branch1.branch1_id = view_inner_zj_devunreg_2.l4_id
	group by bid1;

drop view if exists view_inner_zj_devunreg_4;
create view view_inner_zj_devunreg_4
as
select left(l4_id, 2) as l2_id, count_num 
	from view_inner_zj_devunreg_2
	where l4_id not in (select branch1_id from branch1);

drop view if exists view_inner_zj_devunreg_5;
create view view_inner_zj_devunreg_5
as
select branch1_id as bid1, branch1_name as name,sum(count_num) as devunreg
	from view_inner_zj_devunreg_4 join branch1
		on branch1.branch1_id = view_inner_zj_devunreg_4.l2_id
	group by bid1;

drop view if exists view_inner_zj_devunreg;
create view view_inner_zj_devunreg
as
select * from view_inner_zj_devunreg_3
union
(select * from view_inner_zj_devunreg_5)
	order by bid1;

/* ------------------------- 5 ------------------------- */
/*
思路：
1. 从 devstate_base 表中选出有重复设备的机构
2. 计算出重复设备数量
3. 用机构编号前四位与表一join选出有重复设备的一级分行
4. 把机构编号前四位中在第三步中没有使用过的筛选出来，并取编号的前两位
5. 用第四步得出的视图与表一join选出有重复设备的一级分行
6. 把第三步与第五步得出的结果union出来并排序
*/

/* 1 */
drop view if exists view_inner_zj_devdup_0;
create view view_inner_zj_devdup_0
as
select devstate_base_devid, count(devstate_base_devid) as count_num
	from devstate_base
	group by devstate_base_devid;
/* 2 */
drop view if exists view_inner_zj_devdup_1;
create view view_inner_zj_devdup_1
as
select left(devstate_base_devid, 4) as l4_id, (count_num-1) as count_num
	from view_inner_zj_devdup_0
	where count_num > 1;
/* 3 */
drop view if exists view_inner_zj_devdup_2;
create view view_inner_zj_devdup_2
as
select branch1_id as bid1, branch1_name as name, sum(count_num) as devdup
	from view_inner_zj_devdup_1 join branch1
		on branch1.branch1_id = view_inner_zj_devdup_1.l4_id
	group by bid1;
/* 4 */
drop view if exists view_inner_zj_devdup_3;
create view view_inner_zj_devdup_3
as
select left(l4_id, 2) as l2_id, count_num
	from view_inner_zj_devdup_1
	where l4_id not in (select branch1_id from branch1);
/* 5 */
drop view if exists view_inner_zj_devdup_4;
create view view_inner_zj_devdup_4
as
select branch1_id as bid1, branch1_name as name, sum(count_num) as devdup
	from view_inner_zj_devdup_3 join branch1
		on branch1.branch1_id = view_inner_zj_devdup_3.l2_id
	group by bid1;
/* 6 */
drop view if exists view_inner_zj_devdup;
create view view_inner_zj_devdup
as
select * from view_inner_zj_devdup_2
union
(select * from view_inner_zj_devdup_4)
	order by bid1;

/* ------------------------- 6 ------------------------- */
drop view if exists view_devorg_zj_0;
create view view_devorg_zj_0
as
select view_inner_zj_bid2num.bid1 as bid1, view_inner_zj_bid2num.name as name,
	bid2num, devnum
from view_inner_zj_bid2num left outer join view_inner_zj_devnum
	on view_inner_zj_bid2num.bid1 = view_inner_zj_devnum.bid1;

drop view if exists view_devorg_zj_1;
create view view_devorg_zj_1
as
select view_devorg_zj_0.bid1 as bid1, view_devorg_zj_0.name,
	bid2num, devnum, devcount
from view_devorg_zj_0 left outer join view_inner_zj_devcount
	on view_devorg_zj_0.bid1 = view_inner_zj_devcount.bid1;

drop view if exists view_devorg_zj_2;
create view view_devorg_zj_2
as
select view_devorg_zj_1.bid1 as bid1, view_devorg_zj_1.name,
	bid2num, devnum, devcount, devunreg
from view_devorg_zj_1 left outer join view_inner_zj_devunreg
	on view_devorg_zj_1.bid1 = view_inner_zj_devunreg.bid1;

drop view if exists view_devorg_zj;
create view view_devorg_zj
as
select view_devorg_zj_2.bid1 as bid1, view_devorg_zj_2.name,
	ifnull(bid2num, 0) as bid2num,
	ifnull(devnum, 0) as devnum,
	ifnull(devcount, 0) as devcount,
	ifnull(devunreg, 0) as devunreg,
	ifnull(devdup, 0) as devdup
from view_devorg_zj_2 left outer join view_inner_zj_devdup
	on view_devorg_zj_2.bid1 = view_inner_zj_devdup.bid1;

/* ------------------------- check ------------------------- */
select * from view_inner_zj_bid2num;
select * from view_inner_zj_devnum;
select * from view_inner_zj_devcount;
select * from view_inner_zj_devunreg;
select * from view_inner_zj_devdup;
select * from view_devorg_zj;
