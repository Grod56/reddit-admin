CREATE TABLE PostInfo (
    id          VARCHAR PRIMARY KEY
                        NOT NULL,
    Title       VARCHAR NOT NULL,
    TimeCreated INTEGER NOT NULL
);

CREATE TABLE SubmissionReplyDetails (
    url    VARCHAR NOT NULL
                   PRIMARY KEY,
    reply  VARCHAR NOT NULL,
    oneoff BOOLEAN NOT NULL
);

CREATE TABLE SubmissionReplyerCommented (
    commentId VARCHAR PRIMARY KEY
                      NOT NULL,
    url       VARCHAR REFERENCES SubmissionReplyDetails (url) ON DELETE CASCADE
                                                         ON UPDATE CASCADE
);