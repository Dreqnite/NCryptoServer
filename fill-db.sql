-- Fills the table 'client' with testing data
INSERT INTO client (id, login, password, name, info) VALUES (1, 'John', '1111', 'Ivan Ivanov', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (2, 'Fedya', '2222', 'Fedor Fedorov', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (3, 'Petr', '3333', 'Petr Petrov', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (4, 'Andy', '4444', 'Andrew Krylov', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (5, 'Kostya', '5555', 'Konstantin Konstantinov', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (6, 'Olga', '6666', 'Olga Olegova', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (7, 'Ruslan', '7777', 'Ruslan Ruslanov', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (8, 'Ira', '8888', 'Irina Romanova', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (9, 'Nastya', '9999', 'Anastasiya Belova', NULL);
INSERT INTO client (id, login, password, name, info) VALUES (10, 'Yarik', 'qwer', 'Yaroslav Fedosov', NULL);

-- Fills the table 'client_contacts' with testing data
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (1, 1, 2);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (2, 2, 1);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (3, 2, 3);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (4, 3, 2);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (5, 3, 4);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (6, 4, 3);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (7, 4, 5);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (8, 5, 4);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (9, 5, 6);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (10, 6, 5);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (11, 6, 7);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (12, 7, 6);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (13, 7, 8);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (14, 8, 7);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (15, 8, 9);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (16, 9, 8);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (17, 9, 10);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (18, 10, 9);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (19, 4, 10);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (20, 10, 4);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (21, 4, 8);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (22, 8, 4);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (23, 4, 6);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (24, 6, 4);

INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (25, 4, 7);
INSERT INTO client_contacts (id, id_client_one, id_client_two) VALUES (26, 7, 4);

-- Fills the table 'chatroom' with testing data
INSERT INTO chatroom (id, name) VALUES (1, '#Python');
INSERT INTO chatroom (id, name) VALUES (2, '#hh');
INSERT INTO chatroom (id, name) VALUES (3, '#CppCon');
INSERT INTO chatroom (id, name) VALUES (4, '#StackOverflow');

-- Fills the table 'chatroom_client' with testing data
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (2, 4, 2);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (4, 4, 4);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (5, 5, 1);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (7, 7, 1);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (8, 8, 1);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (9, 9, 1);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (10, 10, 1);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (13, 4, 1);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (14, 6, 1);
INSERT INTO chatroom_client (id, id_client, id_chatroom) VALUES (15, 4, 3);