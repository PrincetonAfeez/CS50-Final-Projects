-- Resume Builder schema for SQLite3

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE CHECK (email LIKE '%_@_%._%'),
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    city TEXT,
    state_region TEXT,
    country TEXT,
    headline TEXT,
    professional_summary TEXT,
    website_url TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    target_role TEXT,
    summary_override TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, name)
);

CREATE TABLE experiences (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    employer TEXT NOT NULL,
    job_title TEXT NOT NULL,
    location TEXT,
    employment_type TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (
        employment_type IS NULL
        OR employment_type IN (
            'full-time',
            'part-time',
            'contract',
            'internship',
            'freelance',
            'temporary'
        )
    ),
    CHECK (date(start_date) IS NOT NULL),
    CHECK (end_date IS NULL OR date(end_date) IS NOT NULL),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE experience_bullets (
    id INTEGER PRIMARY KEY,
    experience_id INTEGER NOT NULL,
    display_order INTEGER NOT NULL CHECK (display_order > 0),
    bullet_text TEXT NOT NULL CHECK (length(trim(bullet_text)) > 0),
    FOREIGN KEY (experience_id) REFERENCES experiences(id) ON DELETE CASCADE
);

CREATE TABLE educations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    school_name TEXT NOT NULL,
    degree TEXT,
    field_of_study TEXT,
    location TEXT,
    start_date TEXT,
    end_date TEXT,
    gpa REAL CHECK (gpa IS NULL OR (gpa >= 0.0 AND gpa <= 4.5)),
    honors TEXT,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (start_date IS NULL OR date(start_date) IS NOT NULL),
    CHECK (end_date IS NULL OR date(end_date) IS NOT NULL),
    CHECK (start_date IS NULL OR end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    role TEXT,
    organization TEXT,
    url TEXT,
    start_date TEXT,
    end_date TEXT,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (start_date IS NULL OR date(start_date) IS NOT NULL),
    CHECK (end_date IS NULL OR date(end_date) IS NOT NULL),
    CHECK (start_date IS NULL OR end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE certifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    issuer TEXT NOT NULL CHECK (length(trim(issuer)) > 0),
    issue_date TEXT NOT NULL,
    expiration_date TEXT,
    credential_id TEXT,
    credential_url TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (date(issue_date) IS NOT NULL),
    CHECK (expiration_date IS NULL OR date(expiration_date) IS NOT NULL),
    CHECK (expiration_date IS NULL OR expiration_date >= issue_date)
);

CREATE TABLE "references" (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0),
    relationship TEXT,
    company TEXT,
    email TEXT CHECK (email IS NULL OR email LIKE '%_@_%._%'),
    phone TEXT,
    note TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(trim(name)) > 0)
);

CREATE TABLE resume_items (
    id INTEGER PRIMARY KEY,
    resume_id INTEGER NOT NULL,
    experience_id INTEGER,
    education_id INTEGER,
    project_id INTEGER,
    certification_id INTEGER,
    reference_id INTEGER,
    skill_id INTEGER,
    display_order INTEGER NOT NULL CHECK (display_order > 0),
    proficiency_level TEXT,
    years_experience REAL,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    FOREIGN KEY (experience_id) REFERENCES experiences(id) ON DELETE CASCADE,
    FOREIGN KEY (education_id) REFERENCES educations(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (certification_id) REFERENCES certifications(id) ON DELETE CASCADE,
    FOREIGN KEY (reference_id) REFERENCES "references"(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE (resume_id, experience_id),
    UNIQUE (resume_id, education_id),
    UNIQUE (resume_id, project_id),
    UNIQUE (resume_id, certification_id),
    UNIQUE (resume_id, reference_id),
    UNIQUE (resume_id, skill_id),
    CHECK (
        (CASE WHEN experience_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN education_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN project_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN certification_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN reference_id IS NOT NULL THEN 1 ELSE 0 END) +
        (CASE WHEN skill_id IS NOT NULL THEN 1 ELSE 0 END) = 1
    ),
    CHECK (
        (skill_id IS NOT NULL
            AND proficiency_level IN ('beginner', 'intermediate', 'advanced', 'expert')
            AND (years_experience IS NULL OR years_experience >= 0))
        OR
        (skill_id IS NULL
            AND proficiency_level IS NULL
            AND years_experience IS NULL)
    )
);

CREATE INDEX idx_experiences_user_id ON experiences(user_id);
CREATE INDEX idx_experience_bullets_experience_id ON experience_bullets(experience_id);
CREATE INDEX idx_resume_items_resume_order ON resume_items(resume_id, display_order);

CREATE VIEW v_resume_full AS
SELECT
    r.id AS resume_id,
    r.user_id,
    r.name AS resume_name,
    ri.display_order,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN 'experience'
        WHEN ri.education_id IS NOT NULL THEN 'education'
        WHEN ri.project_id IS NOT NULL THEN 'project'
        WHEN ri.certification_id IS NOT NULL THEN 'certification'
        WHEN ri.reference_id IS NOT NULL THEN 'reference'
        WHEN ri.skill_id IS NOT NULL THEN 'skill'
    END AS item_type,
    COALESCE(
        ri.experience_id,
        ri.education_id,
        ri.project_id,
        ri.certification_id,
        ri.reference_id,
        ri.skill_id
    ) AS item_id,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN e.job_title
        WHEN ri.education_id IS NOT NULL THEN COALESCE(ed.degree, ed.school_name)
        WHEN ri.project_id IS NOT NULL THEN p.name
        WHEN ri.certification_id IS NOT NULL THEN c.name
        WHEN ri.reference_id IS NOT NULL THEN rf.full_name
        WHEN ri.skill_id IS NOT NULL THEN s.name
    END AS title,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN e.employer
        WHEN ri.education_id IS NOT NULL THEN ed.school_name
        WHEN ri.project_id IS NOT NULL THEN p.organization
        WHEN ri.certification_id IS NOT NULL THEN c.issuer
        WHEN ri.reference_id IS NOT NULL THEN rf.company
        WHEN ri.skill_id IS NOT NULL THEN NULL
    END AS organization,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN e.employment_type
        WHEN ri.education_id IS NOT NULL THEN ed.field_of_study
        WHEN ri.project_id IS NOT NULL THEN p.role
        WHEN ri.certification_id IS NOT NULL THEN c.credential_id
        WHEN ri.reference_id IS NOT NULL THEN rf.relationship
        WHEN ri.skill_id IS NOT NULL THEN ri.proficiency_level
    END AS subtitle,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN e.location
        WHEN ri.education_id IS NOT NULL THEN ed.location
        ELSE NULL
    END AS location,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN e.start_date
        WHEN ri.education_id IS NOT NULL THEN ed.start_date
        WHEN ri.project_id IS NOT NULL THEN p.start_date
        WHEN ri.certification_id IS NOT NULL THEN c.issue_date
        ELSE NULL
    END AS start_date,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN e.end_date
        WHEN ri.education_id IS NOT NULL THEN ed.end_date
        WHEN ri.project_id IS NOT NULL THEN p.end_date
        WHEN ri.certification_id IS NOT NULL THEN c.expiration_date
        ELSE NULL
    END AS end_date,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN e.description
        WHEN ri.education_id IS NOT NULL THEN ed.description
        WHEN ri.project_id IS NOT NULL THEN p.description
        WHEN ri.certification_id IS NOT NULL THEN c.credential_url
        WHEN ri.reference_id IS NOT NULL THEN rf.note
        WHEN ri.skill_id IS NOT NULL THEN NULL
    END AS body,
    CASE
        WHEN ri.skill_id IS NOT NULL THEN ri.years_experience
        ELSE NULL
    END AS years_experience,
    CASE
        WHEN ri.reference_id IS NOT NULL THEN rf.email
        ELSE NULL
    END AS contact_email,
    CASE
        WHEN ri.reference_id IS NOT NULL THEN rf.phone
        ELSE NULL
    END AS contact_phone,
    CASE
        WHEN ri.experience_id IS NOT NULL THEN (
            SELECT group_concat(ordered_bullets.bullet_text, char(10))
            FROM (
                SELECT bullet_text
                FROM experience_bullets
                WHERE experience_id = ri.experience_id
                ORDER BY display_order
            ) AS ordered_bullets
        )
        ELSE NULL
    END AS bullets
FROM resumes AS r
JOIN resume_items AS ri
    ON ri.resume_id = r.id
LEFT JOIN experiences AS e
    ON ri.experience_id = e.id
LEFT JOIN educations AS ed
    ON ri.education_id = ed.id
LEFT JOIN projects AS p
    ON ri.project_id = p.id
LEFT JOIN certifications AS c
    ON ri.certification_id = c.id
LEFT JOIN "references" AS rf
    ON ri.reference_id = rf.id
LEFT JOIN skills AS s
    ON ri.skill_id = s.id;

CREATE VIEW v_career_summary AS
SELECT
    u.id AS user_id,
    u.first_name,
    u.last_name,
    COALESCE(
        (
            SELECT ROUND(
                SUM(
                    julianday(COALESCE(e.end_date, DATE('now'))) - julianday(e.start_date)
                ) / 365.25,
                2
            )
            FROM experiences AS e
            WHERE e.user_id = u.id
        ),
        0
    ) AS total_years_experience,
    (
        SELECT COUNT(*)
        FROM experiences AS e
        WHERE e.user_id = u.id
    ) AS total_jobs,
    COALESCE(
        (
            SELECT COUNT(DISTINCT ri.skill_id)
            FROM resumes AS r
            JOIN resume_items AS ri
                ON ri.resume_id = r.id
            WHERE r.user_id = u.id
              AND ri.skill_id IS NOT NULL
        ),
        0
    ) AS total_skills
FROM users AS u;
