--name: fb
--depends on: None

-- SCHEMA
create table fb_feedback_status(
	status_id int primary key,
	description varchar not null
);

create table fb_feedback_type(
	type_id int primary key,
	description varchar not null
);

create table fb_feedback(
	feedback_id int primary key,
	status_id int not null references fb_feedback_status(status_id),
	type_id int not null references fb_feedback_type(type_id),
	submitted_by_user varchar not null,
	assigned_to_user varchar,
	url varchar not null,
	datetime timestamp not null,		
	description varchar
);

create sequence fb_feedback_id;
---------------------------------------------------
-- INIT DATA
insert into fb_feedback_status(status_id, description)
select 1, 'open' union
select 2, 'closed (fixed)' union
select 3, 'closed (not a bug)' union
select 4, 'closed (won''t fix)' union
select 5, 'working on'
;

insert into fb_feedback_type(type_id, description)
select 1, 'bug' union
select 2, 'suggestion'
;
---------------------------------------------------
-- DESTROY SCHEMA AND DATA
drop table fb_feedback;
drop table fb_feedback_status;
drop table fb_feedback_type;
drop sequence fb_feedback_id;
---------------------------------------------------
-- USE CASES
-- sample data

---------------------------------------------------
--OTHERS
select * from fb_feedback_status;
select * from fb_feedback_type;
select * from fb_feedback;
---------------------------------------------------
---------------------------------------------------
