------------------------------------------------------------------------------
-- Table 'client' contains infomation about chat users.
------------------------------------------------------------------------------
CREATE TABLE client (
    id       INTEGER      PRIMARY KEY
                          NOT NULL,
    login    VARCHAR (32) NOT NULL
                          UNIQUE,
    password VARCHAR (32) NOT NULL,
    name     VARCHAR (32) NOT NULL
                          DEFAULT Anonymous,
    info     VARCHAR (32) 
);

------------------------------------------------------------------------------
-- Table 'client_contacts' holds pairs: client and his contact.
------------------------------------------------------------------------------
CREATE TABLE client_contacts (
    id            INTEGER PRIMARY KEY
                          NOT NULL,
    id_client_one INTEGER NOT NULL
                          REFERENCES client (id) ON DELETE CASCADE
                                                 ON UPDATE CASCADE,
    id_client_two INTEGER NOT NULL
                          REFERENCES client (id),
    CONSTRAINT U_contact UNIQUE (
        id_client_one,
        id_client_two
    )
);

------------------------------------------------------------------------------
-- Table 'chatroom' contains information about chatrooms.
------------------------------------------------------------------------------
CREATE TABLE chatroom (
    id   INTEGER      PRIMARY KEY
                      NOT NULL,
    name VARCHAR (32) UNIQUE
);

------------------------------------------------------------------------------
-- Associative table 'chatroom_client' implements 'many-to-many' relationship
-- between tables: 'chatroom' and 'client', as many clients can be in many
-- chatrooms.
------------------------------------------------------------------------------
CREATE TABLE chatroom_client (
    id          INTEGER PRIMARY KEY
                        NOT NULL,
    id_client   INTEGER REFERENCES client (id) ON DELETE CASCADE
                                               ON UPDATE CASCADE
                        NOT NULL,
    id_chatroom INTEGER REFERENCES chatroom (id) ON DELETE CASCADE
                                                 ON UPDATE CASCADE
                        NOT NULL
);

------------------------------------------------------------------------------
-- Table 'client_history' holds clients messages.
------------------------------------------------------------------------------
CREATE TABLE client_history (
    id              INTEGER      PRIMARY KEY
                                 NOT NULL,
    connection_time DATETIME     NOT NULL,
    ip              VARCHAR (16) NOT NULL,
    id_client       INTEGER      REFERENCES client (id) ON DELETE CASCADE
                                                        ON UPDATE CASCADE
                                 NOT NULL
);

------------------------------------------------------------------------------
-- Table 'message' holds clients messages.
------------------------------------------------------------------------------
CREATE TABLE message (
    id          INTEGER       NOT NULL
                              PRIMARY KEY,
    from_client VARCHAR (32)  NOT NULL
                              REFERENCES client (login),
    to_client   VARCHAR (32)  REFERENCES client (login) ON DELETE NO ACTION
                                                        ON UPDATE NO ACTION,
    to_chatroom VARCHAR (32)  REFERENCES chatroom (name) ON DELETE NO ACTION
                                                         ON UPDATE NO ACTION,
    message     VARCHAR (128) NOT NULL,
    CONSTRAINT CK_recepient CHECK ( (to_client IS NOT NULL AND 
                                     to_chatroom IS NULL) OR 
                                    (to_client IS NULL AND 
                                     to_chatroom IS NOT NULL) ) 
);