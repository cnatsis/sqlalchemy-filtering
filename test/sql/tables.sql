-- User info
create table user_info
(
    id            serial primary key,
    details       jsonb,
    creation_date timestamp not null
);

create index ix_user_info_id
    on user_info (id);

create table user_info
(
    id            serial
        primary key,
    details       jsonb,
    creation_date timestamp not null
);

alter table user_info
    owner to postgres;

create index ix_user_info_id
    on user_info (id);

INSERT INTO public.user_info (id, details, creation_date) VALUES (1, '{"skin": "White", "gender": "Male", "height": 180, "weight": 80, "ref_date": "2021-10-11", "last_name": "Wick", "first_name": "John", "user_details": [{"skill": "Fighting", "rating": 10}, {"skill": "Driving", "rating": 7}], "marital_status": "Single (never married)"}', '2021-12-24 17:12:56.000000');
INSERT INTO public.user_info (id, details, creation_date) VALUES (2, '{"skin": "White", "gender": "Male", "height": 188, "weight": 78, "ref_date": "2013-11-30", "last_name": "Walker", "first_name": "Paul", "user_details": [{"skill": "Fighting", "rating": 7}, {"skill": "Driving", "rating": 10}], "marital_status": "Single (never married)"}', '2021-12-10 17:13:33.000000');
INSERT INTO public.user_info (id, details, creation_date) VALUES (3, '{"skin": "White", "gender": "Male", "height": 176, "weight": 84, "ref_date": "2019-08-19", "last_name": "Di Caprio", "first_name": "Leonardo", "user_details": [{"skill": "Fighting", "rating": 5}, {"skill": "Driving", "rating": 6}], "marital_status": "Single (never married)"}', '2021-11-28 17:13:50.000000');

-- Ratings
create table ratings
(
    id            serial primary key,
    creation_date timestamp not null,
    movie_name    varchar,
    rating        double
);

create index ix_ratings_id
    on ratings (id);

create table ratings
(
    id            serial
        primary key,
    creation_date timestamp not null,
    movie_name    varchar,
    rating        real
);

alter table ratings
    owner to postgres;

create index ix_ratings_id
    on ratings (id);

INSERT INTO public.ratings (id, creation_date, movie_name, rating) VALUES (1, '2021-12-24 17:14:34.000000', 'The Wolf of Wall Street', 8.2);
INSERT INTO public.ratings (id, creation_date, movie_name, rating) VALUES (2, '2021-07-24 17:14:36.000000', 'The Dark Knight', 9);
INSERT INTO public.ratings (id, creation_date, movie_name, rating) VALUES (3, '2021-05-26 17:14:41.000000', 'Transformers', 7);

