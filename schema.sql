CREATE TABLE users (
    id integer primary key autoincrement,
    username text not null unique,
    password text not null,
    expert boolean not null,
    admin boolean not null
);

CREATE TABLE questions (
    id integer primary key autoincrement,
    question_text text not null,
    answer text,
    asked_by_id integer not null,
    expert_id integer not null,
    foreign key(asked_by_id) references users(id),
    foreign key(expert_id) references users(id)
);