create database if not exists kpireport;

create table kpireport.signups (
    created_at datetime not null
);

--- Generated via generate_timeseries.py helper script ---

insert into kpireport.signups (created_at)
values
  {values}