-- Default Categories for Personal Finance Dashboard
-- Common income, expense, and transfer categories
-- NOTE: Parent categories must be inserted before their children

-- ===================================================
-- PARENT INCOME CATEGORIES
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Income', NULL, 'income', '💰', '#10B981', 'All income sources');

-- Child income categories
INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Salary', (SELECT id FROM categories WHERE name = 'Income'), 'income', '💵', '#10B981', 'Employment salary and wages'),
    ('Freelance', (SELECT id FROM categories WHERE name = 'Income'), 'income', '💼', '#10B981', 'Freelance and contract work'),
    ('Investment Income', (SELECT id FROM categories WHERE name = 'Income'), 'income', '📈', '#10B981', 'Dividends, interest, capital gains'),
    ('Rental Income', (SELECT id FROM categories WHERE name = 'Income'), 'income', '🏠', '#10B981', 'Income from rental properties'),
    ('Business Income', (SELECT id FROM categories WHERE name = 'Income'), 'income', '🏢', '#10B981', 'Business revenue'),
    ('Gifts', (SELECT id FROM categories WHERE name = 'Income'), 'income', '🎁', '#10B981', 'Money received as gifts'),
    ('Refunds', (SELECT id FROM categories WHERE name = 'Income'), 'income', '↩️', '#10B981', 'Tax refunds, purchase refunds'),
    ('Other Income', (SELECT id FROM categories WHERE name = 'Income'), 'income', '💲', '#10B981', 'Other income sources');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Housing
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Housing', NULL, 'expense', '🏡', '#EF4444', 'Housing-related expenses');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Rent/Mortgage', (SELECT id FROM categories WHERE name = 'Housing'), 'expense', '🏘️', '#EF4444', 'Monthly rent or mortgage payment'),
    ('Property Tax', (SELECT id FROM categories WHERE name = 'Housing'), 'expense', '🏛️', '#EF4444', 'Property taxes'),
    ('Home Insurance', (SELECT id FROM categories WHERE name = 'Housing'), 'expense', '🛡️', '#EF4444', 'Homeowners or renters insurance'),
    ('Home Maintenance', (SELECT id FROM categories WHERE name = 'Housing'), 'expense', '🔧', '#EF4444', 'Repairs and maintenance'),
    ('HOA Fees', (SELECT id FROM categories WHERE name = 'Housing'), 'expense', '🏘️', '#EF4444', 'Homeowners association fees');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Utilities
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Utilities', NULL, 'expense', '💡', '#F59E0B', 'Utility bills');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Electricity', (SELECT id FROM categories WHERE name = 'Utilities'), 'expense', '⚡', '#F59E0B', 'Electric bill'),
    ('Gas', (SELECT id FROM categories WHERE name = 'Utilities'), 'expense', '🔥', '#F59E0B', 'Natural gas bill'),
    ('Water', (SELECT id FROM categories WHERE name = 'Utilities'), 'expense', '💧', '#F59E0B', 'Water and sewer'),
    ('Internet', (SELECT id FROM categories WHERE name = 'Utilities'), 'expense', '🌐', '#F59E0B', 'Internet service'),
    ('Phone', (SELECT id FROM categories WHERE name = 'Utilities'), 'expense', '📱', '#F59E0B', 'Mobile and landline phone'),
    ('Cable/Streaming', (SELECT id FROM categories WHERE name = 'Utilities'), 'expense', '📺', '#F59E0B', 'TV and streaming services'),
    ('Trash', (SELECT id FROM categories WHERE name = 'Utilities'), 'expense', '🗑️', '#F59E0B', 'Garbage and recycling');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Transportation
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Transportation', NULL, 'expense', '🚗', '#3B82F6', 'Transportation costs');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Gas/Fuel', (SELECT id FROM categories WHERE name = 'Transportation'), 'expense', '⛽', '#3B82F6', 'Vehicle fuel'),
    ('Car Payment', (SELECT id FROM categories WHERE name = 'Transportation'), 'expense', '🚙', '#3B82F6', 'Auto loan payment'),
    ('Car Insurance', (SELECT id FROM categories WHERE name = 'Transportation'), 'expense', '🛡️', '#3B82F6', 'Vehicle insurance'),
    ('Car Maintenance', (SELECT id FROM categories WHERE name = 'Transportation'), 'expense', '🔧', '#3B82F6', 'Repairs and maintenance'),
    ('Parking', (SELECT id FROM categories WHERE name = 'Transportation'), 'expense', '🅿️', '#3B82F6', 'Parking fees and tolls'),
    ('Public Transit', (SELECT id FROM categories WHERE name = 'Transportation'), 'expense', '🚇', '#3B82F6', 'Bus, train, subway'),
    ('Rideshare', (SELECT id FROM categories WHERE name = 'Transportation'), 'expense', '🚕', '#3B82F6', 'Uber, Lyft, taxis');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Food & Dining
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Food & Dining', NULL, 'expense', '🍽️', '#8B5CF6', 'Food and dining expenses');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Groceries', (SELECT id FROM categories WHERE name = 'Food & Dining'), 'expense', '🛒', '#8B5CF6', 'Grocery shopping'),
    ('Restaurants', (SELECT id FROM categories WHERE name = 'Food & Dining'), 'expense', '🍴', '#8B5CF6', 'Dining out'),
    ('Coffee Shops', (SELECT id FROM categories WHERE name = 'Food & Dining'), 'expense', '☕', '#8B5CF6', 'Coffee and cafes'),
    ('Fast Food', (SELECT id FROM categories WHERE name = 'Food & Dining'), 'expense', '🍔', '#8B5CF6', 'Fast food and takeout'),
    ('Alcohol/Bars', (SELECT id FROM categories WHERE name = 'Food & Dining'), 'expense', '🍺', '#8B5CF6', 'Alcoholic beverages');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Healthcare
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Healthcare', NULL, 'expense', '⚕️', '#EC4899', 'Medical and health expenses');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Health Insurance', (SELECT id FROM categories WHERE name = 'Healthcare'), 'expense', '🏥', '#EC4899', 'Health insurance premiums'),
    ('Doctor', (SELECT id FROM categories WHERE name = 'Healthcare'), 'expense', '👨‍⚕️', '#EC4899', 'Doctor visits and copays'),
    ('Dentist', (SELECT id FROM categories WHERE name = 'Healthcare'), 'expense', '🦷', '#EC4899', 'Dental care'),
    ('Pharmacy', (SELECT id FROM categories WHERE name = 'Healthcare'), 'expense', '💊', '#EC4899', 'Prescriptions and medications'),
    ('Vision', (SELECT id FROM categories WHERE name = 'Healthcare'), 'expense', '👓', '#EC4899', 'Eye care and glasses'),
    ('Mental Health', (SELECT id FROM categories WHERE name = 'Healthcare'), 'expense', '🧠', '#EC4899', 'Therapy and counseling'),
    ('Gym/Fitness', (SELECT id FROM categories WHERE name = 'Healthcare'), 'expense', '💪', '#EC4899', 'Gym membership and fitness');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Shopping
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Shopping', NULL, 'expense', '🛍️', '#14B8A6', 'Shopping and personal items');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Clothing', (SELECT id FROM categories WHERE name = 'Shopping'), 'expense', '👔', '#14B8A6', 'Clothes and accessories'),
    ('Electronics', (SELECT id FROM categories WHERE name = 'Shopping'), 'expense', '💻', '#14B8A6', 'Electronics and gadgets'),
    ('Home Goods', (SELECT id FROM categories WHERE name = 'Shopping'), 'expense', '🛋️', '#14B8A6', 'Furniture and home decor'),
    ('Personal Care', (SELECT id FROM categories WHERE name = 'Shopping'), 'expense', '💄', '#14B8A6', 'Haircuts, cosmetics, toiletries'),
    ('Hobbies', (SELECT id FROM categories WHERE name = 'Shopping'), 'expense', '🎨', '#14B8A6', 'Hobby supplies and equipment');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Entertainment
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Entertainment', NULL, 'expense', '🎬', '#F97316', 'Entertainment and recreation');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Movies/Theater', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '🎭', '#F97316', 'Movies and performances'),
    ('Concerts/Events', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '🎵', '#F97316', 'Concerts and events'),
    ('Subscriptions', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '📱', '#F97316', 'Digital subscriptions'),
    ('Gaming', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '🎮', '#F97316', 'Video games'),
    ('Books', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '📚', '#F97316', 'Books and magazines'),
    ('Sports', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '⚽', '#F97316', 'Sports activities and equipment'),
    ('Travel', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '✈️', '#F97316', 'Vacations and trips'),
    ('Pets', (SELECT id FROM categories WHERE name = 'Entertainment'), 'expense', '🐕', '#F97316', 'Pet care and supplies');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Education
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Education', NULL, 'expense', '🎓', '#6366F1', 'Education expenses');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Tuition', (SELECT id FROM categories WHERE name = 'Education'), 'expense', '🏫', '#6366F1', 'School tuition'),
    ('Books/Supplies', (SELECT id FROM categories WHERE name = 'Education'), 'expense', '📖', '#6366F1', 'Educational materials'),
    ('Student Loans', (SELECT id FROM categories WHERE name = 'Education'), 'expense', '🎓', '#6366F1', 'Student loan payments'),
    ('Online Courses', (SELECT id FROM categories WHERE name = 'Education'), 'expense', '💻', '#6366F1', 'Online learning platforms');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Personal/Family
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Personal/Family', NULL, 'expense', '👨‍👩‍👧', '#A855F7', 'Personal and family expenses');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Childcare', (SELECT id FROM categories WHERE name = 'Personal/Family'), 'expense', '👶', '#A855F7', 'Daycare and babysitting'),
    ('Child Support', (SELECT id FROM categories WHERE name = 'Personal/Family'), 'expense', '👨‍👩‍👧‍👦', '#A855F7', 'Child support payments'),
    ('Alimony', (SELECT id FROM categories WHERE name = 'Personal/Family'), 'expense', '💍', '#A855F7', 'Alimony payments'),
    ('Life Insurance', (SELECT id FROM categories WHERE name = 'Personal/Family'), 'expense', '🛡️', '#A855F7', 'Life insurance premiums'),
    ('Charity/Donations', (SELECT id FROM categories WHERE name = 'Personal/Family'), 'expense', '❤️', '#A855F7', 'Charitable donations');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Financial
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Financial', NULL, 'expense', '💳', '#059669', 'Financial services and fees');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Bank Fees', (SELECT id FROM categories WHERE name = 'Financial'), 'expense', '🏦', '#059669', 'Banking fees and charges'),
    ('Credit Card Fees', (SELECT id FROM categories WHERE name = 'Financial'), 'expense', '💳', '#059669', 'Credit card annual fees and interest'),
    ('ATM Fees', (SELECT id FROM categories WHERE name = 'Financial'), 'expense', '🏧', '#059669', 'ATM withdrawal fees'),
    ('Investment Fees', (SELECT id FROM categories WHERE name = 'Financial'), 'expense', '📊', '#059669', 'Brokerage and advisory fees'),
    ('Tax Preparation', (SELECT id FROM categories WHERE name = 'Financial'), 'expense', '📋', '#059669', 'Tax filing services'),
    ('Legal Fees', (SELECT id FROM categories WHERE name = 'Financial'), 'expense', '⚖️', '#059669', 'Attorney and legal services');

-- ===================================================
-- PARENT EXPENSE CATEGORIES - Taxes
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Taxes', NULL, 'expense', '🏛️', '#DC2626', 'Tax payments');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Federal Tax', (SELECT id FROM categories WHERE name = 'Taxes'), 'expense', '🏛️', '#DC2626', 'Federal income tax'),
    ('State Tax', (SELECT id FROM categories WHERE name = 'Taxes'), 'expense', '🏛️', '#DC2626', 'State income tax'),
    ('Sales Tax', (SELECT id FROM categories WHERE name = 'Taxes'), 'expense', '🏛️', '#DC2626', 'Sales tax payments');

-- ===================================================
-- UNCATEGORIZED
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Uncategorized', NULL, 'expense', '❓', '#6B7280', 'Uncategorized expenses');

-- ===================================================
-- TRANSFER CATEGORIES
-- ===================================================

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Transfer', NULL, 'transfer', '🔄', '#6B7280', 'Transfers between accounts');

INSERT INTO categories (name, parent_category_id, category_type, icon, color, description) VALUES
    ('Credit Card Payment', (SELECT id FROM categories WHERE name = 'Transfer'), 'transfer', '💳', '#6B7280', 'Payment to credit card'),
    ('Savings Transfer', (SELECT id FROM categories WHERE name = 'Transfer'), 'transfer', '🏦', '#6B7280', 'Transfer to/from savings'),
    ('Investment Transfer', (SELECT id FROM categories WHERE name = 'Transfer'), 'transfer', '📈', '#6B7280', 'Transfer to/from investment account');
