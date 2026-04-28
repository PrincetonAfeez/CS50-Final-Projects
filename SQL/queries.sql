-- Representative runnable queries for Resume Builder
-- Usage (SQLite CLI):
--   .read schema.sql
--   .read queries.sql

-- Seed one user.
INSERT INTO users (
    email,
    password_hash,
    first_name,
    last_name,
    phone,
    city,
    state_region,
    country,
    headline,
    professional_summary,
    website_url,
    linkedin_url,
    github_url
) VALUES (
    'alex.morgan@example.com',
    'argon2id$demo-hash',
    'Alex',
    'Morgan',
    '+1-555-0101',
    'Seattle',
    'WA',
    'USA',
    'Operations and Hospitality Leader',
    'Leads cross-functional teams and improves guest experience through process and service design.',
    'https://alexmorgan.dev',
    'https://linkedin.com/in/alexmorgan',
    'https://github.com/alexmorgan'
);

-- Seed second user (minimal required fields).
INSERT INTO users (
    email,
    password_hash,
    first_name,
    last_name
) VALUES (
    'blake.chen@example.com',
    'argon2id$demo-hash-2',
    'Blake',
    'Chen'
);

-- Seed resumes.
INSERT INTO resumes (user_id, name, is_primary, target_role, summary_override)
VALUES (
    (SELECT id FROM users WHERE email = 'alex.morgan@example.com'),
    'Hospitality GM',
    1,
    'General Manager',
    'Focused on multi-site operations leadership.'
);

INSERT INTO resumes (user_id, name, is_primary, target_role, summary_override)
VALUES (
    (SELECT id FROM users WHERE email = 'alex.morgan@example.com'),
    'Operations Director',
    0,
    'Director of Operations',
    NULL
);

INSERT INTO resumes (user_id, name, is_primary, target_role, summary_override)
VALUES (
    (SELECT id FROM users WHERE email = 'blake.chen@example.com'),
    'Data Analyst',
    1,
    'Data Analyst',
    NULL
);

-- Seed experiences.
INSERT INTO experiences (
    user_id, employer, job_title, location, employment_type, start_date, end_date, description
) VALUES
    ((SELECT id FROM users WHERE email = 'alex.morgan@example.com'), 'Northwind Hotels', 'General Manager', 'Seattle, WA', 'full-time', '2021-06-01', NULL, 'Owned P&L and service quality across a flagship property.'),
    ((SELECT id FROM users WHERE email = 'alex.morgan@example.com'), 'Contoso Restaurants', 'Assistant Manager', 'Portland, OR', 'full-time', '2018-03-01', '2021-05-15', 'Led staffing, scheduling, and front-of-house operations.');

-- Seed bullets.
INSERT INTO experience_bullets (experience_id, display_order, bullet_text) VALUES
    ((SELECT id FROM experiences WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND employer = 'Northwind Hotels' AND job_title = 'General Manager'), 1, 'Improved guest satisfaction score from 4.2 to 4.7 in 12 months.'),
    ((SELECT id FROM experiences WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND employer = 'Northwind Hotels' AND job_title = 'General Manager'), 2, 'Reduced staff turnover by 18 percent through coaching program.'),
    ((SELECT id FROM experiences WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND employer = 'Contoso Restaurants' AND job_title = 'Assistant Manager'), 1, 'Standardized shift handoff process across three locations.');

-- Seed education.
INSERT INTO educations (
    user_id, school_name, degree, field_of_study, location, start_date, end_date, gpa, honors, description
) VALUES (
    (SELECT id FROM users WHERE email = 'alex.morgan@example.com'), 'University of Washington', 'BBA', 'Business Administration', 'Seattle, WA',
    '2013-09-01', '2017-06-15', 3.72, 'Dean''s List', 'Coursework in operations and organizational behavior.'
);

-- Seed projects.
INSERT INTO projects (
    user_id, name, role, organization, url, start_date, end_date, description
) VALUES (
    (SELECT id FROM users WHERE email = 'alex.morgan@example.com'), 'Service Recovery Playbook', 'Lead Author', 'Northwind Hotels',
    'https://example.com/service-playbook', '2022-01-01', '2022-06-01',
    'Created SOPs for rapid issue resolution and escalation.'
);

-- Seed certifications.
INSERT INTO certifications (
    user_id, name, issuer, issue_date, expiration_date, credential_id, credential_url
) VALUES (
    (SELECT id FROM users WHERE email = 'alex.morgan@example.com'), 'ServSafe Manager', 'National Restaurant Association', '2023-02-01', '2028-02-01',
    'SSM-123456', 'https://example.com/credentials/SSM-123456'
);

-- Seed references.
INSERT INTO "references" (
    user_id, full_name, relationship, company, email, phone, note
) VALUES (
    (SELECT id FROM users WHERE email = 'alex.morgan@example.com'), 'Jamie Lee', 'Former Director', 'Northwind Hotels',
    'jamie.lee@example.com', '+1-555-0142', 'Available after 5 PM PT.'
);

-- Seed skills.
INSERT INTO skills (name) VALUES ('Python'), ('SQL'), ('Team Leadership');

-- Attach items to primary resume (resume_id = 1).
INSERT INTO resume_items (
    resume_id, experience_id, education_id, project_id, certification_id, reference_id, skill_id,
    display_order, proficiency_level, years_experience
) VALUES
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), (SELECT id FROM experiences WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND employer = 'Northwind Hotels' AND job_title = 'General Manager'), NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), (SELECT id FROM experiences WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND employer = 'Contoso Restaurants' AND job_title = 'Assistant Manager'), NULL, NULL, NULL, NULL, NULL, 2, NULL, NULL),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), NULL, (SELECT id FROM educations WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND school_name = 'University of Washington' AND degree = 'BBA'), NULL, NULL, NULL, NULL, 3, NULL, NULL),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), NULL, NULL, (SELECT id FROM projects WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Service Recovery Playbook'), NULL, NULL, NULL, 4, NULL, NULL),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), NULL, NULL, NULL, (SELECT id FROM certifications WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'ServSafe Manager'), NULL, NULL, 5, NULL, NULL),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), NULL, NULL, NULL, NULL, (SELECT id FROM "references" WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND full_name = 'Jamie Lee'), NULL, 6, NULL, NULL),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), NULL, NULL, NULL, NULL, NULL, (SELECT id FROM skills WHERE name = 'Python'), 7, 'advanced', 4.5),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), NULL, NULL, NULL, NULL, NULL, (SELECT id FROM skills WHERE name = 'SQL'), 8, 'expert', 6.0),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Hospitality GM'), NULL, NULL, NULL, NULL, NULL, (SELECT id FROM skills WHERE name = 'Team Leadership'), 9, 'expert', 7.0);

-- Attach a smaller set to second resume (resume_id = 2).
INSERT INTO resume_items (
    resume_id, experience_id, education_id, project_id, certification_id, reference_id, skill_id,
    display_order, proficiency_level, years_experience
) VALUES
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Operations Director'), (SELECT id FROM experiences WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND employer = 'Northwind Hotels' AND job_title = 'General Manager'), NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL),
    ((SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com') AND name = 'Operations Director'), NULL, NULL, NULL, NULL, NULL, (SELECT id FROM skills WHERE name = 'SQL'), 2, 'expert', 6.0);

-- Attach SQL to user 2's resume for multi-user analytics.
INSERT INTO resume_items (
    resume_id, experience_id, education_id, project_id, certification_id, reference_id, skill_id,
    display_order, proficiency_level, years_experience
) VALUES (
    (SELECT id FROM resumes WHERE user_id = (SELECT id FROM users WHERE email = 'blake.chen@example.com') AND name = 'Data Analyst'),
    NULL, NULL, NULL, NULL, NULL,
    (SELECT id FROM skills WHERE name = 'SQL'),
    1, 'advanced', 3.0
);

-- Update example.
UPDATE resumes
SET name = 'Hospitality General Manager'
WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com')
  AND name = 'Hospitality GM';

-- Delete/hide example.
DELETE FROM resume_items
WHERE resume_id = (
        SELECT id
        FROM resumes
        WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com')
          AND name = 'Operations Director'
    )
  AND skill_id = (SELECT id FROM skills WHERE name = 'SQL');

-- READS

-- 1) Render full resume in display order.
SELECT
    resume_id,
    user_id,
    resume_name,
    display_order,
    item_type,
    title,
    organization,
    subtitle,
    location,
    start_date,
    end_date,
    body,
    years_experience,
    contact_email,
    contact_phone,
    bullets
FROM v_resume_full
WHERE resume_id = (
    SELECT id
    FROM resumes
    WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com')
      AND name = 'Hospitality General Manager'
)
ORDER BY display_order, item_type;

-- 2) List all resumes for one user.
SELECT
    id,
    name,
    target_role,
    is_primary,
    created_at
FROM resumes
WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com')
ORDER BY is_primary DESC, name;

-- 3) Find all users with a given skill.
SELECT DISTINCT
    u.id,
    u.first_name,
    u.last_name,
    u.email,
    s.name AS skill_name
FROM skills AS s
JOIN resume_items AS ri
    ON ri.skill_id = s.id
JOIN resumes AS r
    ON r.id = ri.resume_id
JOIN users AS u
    ON u.id = r.user_id
WHERE s.name = 'SQL' COLLATE NOCASE
ORDER BY u.last_name, u.first_name;

-- 4) Get skill proficiency and years for one resume.
SELECT
    s.name AS skill_name,
    ri.proficiency_level,
    ri.years_experience
FROM resume_items AS ri
JOIN skills AS s
    ON ri.skill_id = s.id
WHERE ri.resume_id = (
    SELECT id
    FROM resumes
    WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com')
      AND name = 'Hospitality General Manager'
)
ORDER BY ri.years_experience DESC, skill_name;

-- 5) List experiences for one user in reverse chronological order.
SELECT
    employer,
    job_title,
    start_date,
    end_date
FROM experiences
WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com')
ORDER BY start_date DESC;

-- 6) Most popular skills across all users.
SELECT
    s.name AS skill_name,
    COUNT(DISTINCT r.user_id) AS users_with_skill,
    COUNT(*) AS resume_mentions
FROM skills AS s
JOIN resume_items AS ri
    ON ri.skill_id = s.id
JOIN resumes AS r
    ON r.id = ri.resume_id
GROUP BY s.id, s.name
ORDER BY users_with_skill DESC, resume_mentions DESC, skill_name;

-- 7) Use the career summary view for one user.
SELECT *
FROM v_career_summary
WHERE user_id = (SELECT id FROM users WHERE email = 'alex.morgan@example.com');
