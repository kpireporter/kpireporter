create database if not exists reportcard;

create table reportcard.signups (
    created_at datetime not null
);

--- Generated via generate_timeseries.py helper script ---

insert into reportcard.signups (created_at)
values
  {values}