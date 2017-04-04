--name: usr
--depends on: None

-------------------------------------------
--Create schema
create table usr_role(
	role_id int primary key,
	name varchar not null unique,
	description varchar
);

create table usr_user_status(
	status_id int primary key,
	description varchar not null
);

create table usr_user(
	username varchar not null primary key,
	--password can be null... when a user is just
	--created, before any password is assigned.
	password varchar,
	name varchar,	
	email varchar,
	description varchar,
	role_id int references usr_role(role_id),
	lang_code varchar, --2 letter lang_code
	status_id int not null references usr_user_status(status_id)
);

create table usr_url(
	url_id int primary key,
	url varchar not null unique,
	description varchar
);	

create table usr_role_url(
	role_id int not null references usr_role(role_id),
	url_id int not null references usr_url(url_id),
	--0 for False (not allow), 1 for True (allow)
	is_allow int not null,
	primary key(role_id, url_id)
);

create sequence usr_role_id;
create sequence usr_url_id;
-------------------------------------------------
-------------------------------------------------
--INIT DATA
insert into usr_role(role_id, name)
select nextval('usr_role_id'), 'developer' union
select nextval('usr_role_id'), 'admin' union
select nextval('usr_role_id'), 'user';

insert into usr_user_status(status_id, description)
select 1, 'active' union
select 2, 'inactive';

--use urlspider.py instead of this 'hardcoded' approach

--BELOW WILL ONLY WORK AFTER RUNNING URLSPIDER.PY
insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/admin';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/feedback/';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/feedback/browse';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/feedback/_/';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/feedback/_/details';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/feedback/_/modify';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/feedback/_/delete';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/browse';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/create';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/_/';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/_/details';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/_/modify';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/_/setpassword';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'user'
and u.url = '/cm/user/_/delete';

--ADMIN (for testing)
insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'admin'
and u.url = '/cm/feedback/_/modify';

insert into usr_role_url(role_id, url_id, is_allow)
select r.role_id, u.url_id, 0
from usr_role r, usr_url u
where r.name = 'admin'
and u.url = '/cm/feedback/_/delete';

-------------------------------------------------
-------------------------------------------------
--SAMPLE DATA 
--CREATING NEW USERS, password is 'testing'
insert into usr_user(username, password, name, email,
description, status_id, lang_code, role_id)
select 'alex', 
'dc724af18fbdd4e59189f5fe768a5f8311527050', 'Alex Li', 
'likwoka@yahoo.com', 'Developer', s.status_id, 'fr', r.role_id
from usr_role r, usr_user_status s
where r.name = 'developer'
and s.description = 'active';

insert into usr_user(username, password, name, email, 
description, status_id, lang_code, role_id)
select 'guest', 
'dc724af18fbdd4e59189f5fe768a5f8311527050', 'Guest', null,
'Guest Account', s.status_id, 'en', r.role_id
from usr_role r, usr_user_status s
where r.name = 'user'
and s.description = 'active';


------------------------------------------
-------------------------------------------
--Delete schema
drop table usr_role_url;
drop table usr_url;
drop table usr_user;
drop table usr_user_status;
drop table usr_role; 

drop sequence usr_role_id;
drop sequence usr_url_id;

-------------------------------------------------
-------------------------------------------------

