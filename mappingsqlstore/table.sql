create table test (
    id varchar(128) not null,
    modifier varchar(256),
    field_one varchar(256),
    field_two varchar(256),
    field_three varchar(256),
    primary key (id)
);

insert into test (id, modifier, field_one, field_two, field_three)
    values('monkey', 'cdent', 'fat', 'clean', 'dirt');
