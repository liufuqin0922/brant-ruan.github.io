use yzmon;	/* 把yzmon设置为缺省数据库 */

/* 建立第1小题的view（此处仅为demo，完成作业时删除建立新的即可）*/
drop view if exists view_inner_zj_bid2num;
create view view_inner_zj_bid2num
as
select branch1.branch1_id as bid1, branch1.branch1_name as name ,COUNT(*) as bid2num
       from branch1 
	   left join branch2 on branch1.branch1_id = branch2.branch2_branch1_id
group by bid1
order by bid1;
/* 执行第1小题视图的验证 */
select * from view_inner_zj_bid2num;

/* 建立第2小题的view */
drop view if exists view_inner_zj_devnum;
create view view_inner_zj_devnum
as
select branch1.branch1_id as bid1, branch1.branch1_name as name ,COUNT(*) as devnum
		from branch1, branch2, devorg
where branch1.branch1_id = branch2.branch2_branch1_id and devorg.devorg_branch2_id = branch2.branch2_id
group by bid1 
order by bid1;
/* 执行第2小题视图的验证 */
select * from view_inner_zj_devnum;

/* 建立第3小题的view */
drop view if exists view_inner_zj_devcount;
create view view_inner_zj_devcount
as
select branch1.branch1_id as bid1, branch1.branch1_name as name, COUNT(distinct devstate_base_devid) as devcount
		from devstate_base 
	    inner join devorg on devstate_base.devstate_base_devid = devorg.devorg_id	
        inner join branch2 on branch2.branch2_id = devorg.devorg_branch2_id
	    inner join branch1 on branch2.branch2_branch1_id = branch1.branch1_id
group by bid1
order by bid1;
/* 执行第3小题视图的验证 */
select * from view_inner_zj_devcount;

/* 建立第4小题的view */
drop view if exists tv;
create view tv
as select devstate_base.devstate_base_devid as a 
from devstate_base
where devstate_base.devstate_base_devid not in (select devorg_id from devorg);

drop view if exists view_inner_zj_devunreg;
create view view_inner_zj_devunreg
as
select branch1.branch1_id as bid1, branch1.branch1_name as name, COUNT(a) as devunreg
from branch1 
inner join tv
on left(tv.a,4) = branch1.branch1_id 
	or  (left(tv.a,4) not in (select branch1_id from branch1)  
			and left(tv.a,2) = branch1.branch1_id)
group by branch1.branch1_id
order by bid1;
/* 执行第4小题视图的验证 */
select * from view_inner_zj_devunreg;

/* 建立第5小题的view */
drop view if exists tv5;
create view tv5
as 
select devstate_base_devid as id,COUNT(devstate_base_devno)-1  as num
from devstate_base
group by devstate_base_devid
having num != 0;

drop view if exists view_inner_zj_devdup;
create view view_inner_zj_devdup
as 
select branch1.branch1_id as bid1, branch1.branch1_name as name, sum(tv5.num) as devdup
from branch1
inner join tv5
on left(tv5.id,4) = branch1.branch1_id
    or  (left(tv5.id,4) not in (select branch1_id from branch1)
		and left(tv5.id,2) = branch1.branch1_id)
group by branch1.branch1_id
order by branch1.branch1_id;

/* 执行第5小题视图的验证 */
select * from view_inner_zj_devdup;

/* 建立第6小题的view */
drop view if exists view_devorg_zj;
create view view_devorg_zj
as 
select branch1_id as bid1, branch1_name as name, ifnull(bid2num,0) as bid2num,  
	   ifnull(devnum,0) as devnum, ifnull(devcount,0) as devcount,
	   ifnull(devunreg,0) as devunreg, ifnull(devdup,0) as devdup
from branch1
left join view_inner_zj_bid2num on branch1_id = view_inner_zj_bid2num.bid1 
left join view_inner_zj_devnum on view_inner_zj_devnum.bid1 = branch1_id
left join view_inner_zj_devcount on view_inner_zj_devcount.bid1 = branch1_id
left join view_inner_zj_devunreg on view_inner_zj_devunreg.bid1 = branch1_id
left join view_inner_zj_devdup on view_inner_zj_devdup.bid1 = branch1_id
group by branch1_id
order by branch1_id;
/* 执行第6小题视图的验证 */
select * from view_devorg_zj;
