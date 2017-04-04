--name: ses
--depends on: None

---------------------------------------------------
--CREATE SCHEMA
create table ses_session(
	session_id varchar not null,
	--a pickled session instance.  Can only
	--contains at most 4000 char.  If instance
	--is bigger, then 2 or more rows will be used.
	--The rows will be ordered by the order_ attribute.
	value_ bytea not null,
	----value_ varchar not null,
	
	--the order of the chopped instance.  It should
	--be in ascending order (1,2,3,4).  If the value_
	--stored is the whole session, order_ is 0.
	order_ int not null,
	primary key(session_id, order_)
);


---------------------------------------------------
--DROP SCHEMA
drop table ses_session;


---------------------------------------------------
--TEST DATA
insert into ses_session(session_id, value_, order_)
values ('9223372036854775807', 'abcdef', 1);

insert into ses_session(session_id, value_, order_)
values ('9223372036854775807', 'ghijkl', 2);

insert into ses_session(session_id, value_, order_)
values ('9223372036854775807', 'mnopqr', 3);

insert into ses_session(session_id, value_, order_)
values ('9223372036854776601', 'hello world how are you?', 0);

select * from ses_session;


