--name: core
--depends on: None

create or replace function truncat (text) returns text 
as '
begin
	return substr($1, 1, 64);
end;
' language 'plpgsql';


