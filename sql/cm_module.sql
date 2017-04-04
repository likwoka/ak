--name: cm
--depends on: None

create table cm_obj_type(
	obj_type_id integer primary key,
	description varchar
);

create table cm_obj(
	obj_id bigserial primary key,
	obj_type_id integer not null references cm_obj_type(obj_type_id),
	owner varchar, --this has to be referenced to the other database
	--(possibly in another machine), so we will use a python service
	--to do the referencing... like Prospective Broker in Twisted
	---create_date date not null default current_date,
	---create_time time(0) not null default current_time(0),
	create_datetime timestamp(0),
	---modified_date date,
	---modified_time time(0)
	modify_datetime timestamp(0)
);

create table cm_store(
	store_id integer primary key,
	location varchar,
	security varchar,
	key_holder_access varchar,
	protection_system varchar
) inherits(cm_obj);

create table cm_case_status(
	status_id integer primary key,
	description varchar not null
);

create table cm_incident_status(
	status_id integer primary key,
	description varchar not null
);

create table cm_item_status(
	status_id integer primary key,
	description varchar not null
);

create table cm_incident(
	incident_id integer primary key,
	---incident_date date,
	---incident_time time(0),
	description varchar,
	who varchar,
	date_ date,  --XXX
	time_ time(0),  --XXX
	store_id integer not null references cm_store(store_id),
	narrative varchar,
	outcome varchar,
	service_request varchar,
	status_id integer not null references cm_incident_status(status_id)
) inherits(cm_obj);

create table cm_case(
	case_id integer primary key,
	---case_date date,
	---case_time time(0),
	description varchar,
	hours_expended int, --XXX SHOULD BE HOURS, MINS
	evidence varchar,
	investigation varchar,
	narrative varchar,
	status_id integer not null references cm_case_status(status_id)
) inherits(cm_obj);

create table cm_item(
	item_id integer primary key,
	incident_id integer not null references cm_incident(incident_id),
	description varchar,
	quantity numeric, --XXX 
	amount_value numeric(9,2), --XXX money
	status_id integer not null references cm_item_status(status_id)
) inherits(cm_obj);

create table cm_daily_log(
	daily_log_id integer primary key,
	case_id integer not null references cm_case(case_id),
	date_ date,
	description varchar
) inherits(cm_obj);


create table cm_interview(
--interview/statement
	interview_id integer primary key,
	case_id int not null references cm_case(case_id),
	date_ date not null,
	time_ time(0),
	interviewer varchar,
	interviewee varchar,
	description varchar
) inherits(cm_obj);

create table cm_expense(
	expense_id integer primary key,
	case_id int not null references cm_case(case_id),
	description varchar,
	amount numeric(9,2) --XXX money
) inherits(cm_obj);

/*
create table case_log(
	case_log_id int primary key,
	case_id int not null references cases(case_id),
	status_id int not null references case_status(status_id)
);
*/

create table cm_attachment(
	attachment_id integer primary key,
	filename varchar,
	filetype varchar,
	description varchar,
	size_ integer
) inherits(cm_obj);

create table cm_case_attachment(
	case_id integer not null references cm_case(case_id),
	attachment_id integer not null references cm_attachment(attachment_id),
	primary key(case_id, attachment_id)
);

create table cm_incident_attachment(
	incident_id integer not null references cm_incident(incident_id),
	attachment_id integer not null references cm_attachment(attachment_id),
	primary key(incident_id, attachment_id)
);

create table cm_case_incident(
	case_id integer not null references cm_case(case_id),
	incident_id integer not null references cm_incident(incident_id),
	primary key(case_id, incident_id)
);

create sequence cm_attachment_id;
create sequence cm_incident_id;
create sequence cm_case_id;
create sequence cm_expense_id;
create sequence cm_interview_id;
create sequence cm_daily_log_id;
create sequence cm_item_id;

----------------------------------------------------------------------
----------------------------------------------------------------------
--init data
insert into cm_obj_type(obj_type_id, description)
select 1, 'incident' union
select 2, 'case' union
select 3, 'attachment' union
select 4, 'store' union
select 5, 'item' union
select 6, 'daily_log' union
select 7, 'interview' union
select 8, 'expense'
;

insert into cm_case_status(status_id, description)
select 1, 'open' union
select 2, 'closed'
;

insert into cm_incident_status(status_id, description)
select 1, 'open' union
select 2, 'closed'
;

insert into cm_item_status(status_id, description)
select 1, 'lost' union
select 2, 'recovered'
;
----------------------------------------------------------------------
--sample data
--insert into cm_store(obj_type_id, owner, store_id, location)
--select 4, 'alex', 1, 'Sogo Department Store, Hong Kong' union
--select 4, 'alex', 2, 'Bloor Street, Toronto'
--;

---------------------------------------------------------------
----------------------------------------------------------------------
-- Clean up database
drop table cm_case_attachment;
drop table cm_incident_attachment;
drop table cm_case_incident;
drop table cm_expense;
drop table cm_interview;
drop table cm_daily_log;
drop table cm_item;
drop table cm_attachment;
drop table cm_case_;
drop table cm_incident;
drop table cm_store_;
drop table cm_obj;
drop table cm_item_status;
drop table cm_incident_status;
drop table cm_case_status;
drop table cm_obj_type;

drop sequence cm_attachment_id;
drop sequence cm_incident_id;
drop sequence cm_case_id;
drop sequence cm_expense_id;
drop sequence cm_interview_id;
drop sequence cm_daily_log_id;
drop sequence cm_item_id;
----------------------------------------------------------------------
--installation.... little things to do
--to make the database work with the whole system
--before normal usage.  This should be after the
--schema is created, probably after init data inserted.
-- NOT UP TO DATE!!!
grant all on case_incident to akuser;
grant all on case_ to akuser;
grant all on case_status to akuser;
grant all on incident to akuser;
grant all on store_ to akuser;

----------------------------------------------------------------------
--OTHERS query
select current_date;
select * from case_;
select current_time;
select current_timestamp(0);
select * from store_;
