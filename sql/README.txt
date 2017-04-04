2003 08 15 (postgresql 7.2.4)

Info
====
Database Name: akcm_sampleclient
User: akadmin
Password: (None)


Database Setup
==============
Run on bash prompt, as root:

# createdb -h localhost -U postgres -E UNICODE akcm_sampleclient
# /usr/lib/postgresql/bin/createlang -Upostgres plpgsql akcm_sampleclient

where akcm_sampleclient is the database name.  This means
this database is for the cm application for this client.


