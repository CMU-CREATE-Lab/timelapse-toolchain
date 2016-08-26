import os, sqlite3, json
import settings

db_filename = os.path.join(settings.CURRENT_DIR, 'db', 'projects.db')

def store(params):
	id = params['project_id']
	if 'email' in params:
		email = params['email']
	settings = json.dumps(params)
	select_query = "SELECT COUNT(*) FROM projects WHERE id=?;"
	update_query = "UPDATE projects SET settings=? WHERE id=?;"
	insert_query = "INSERT INTO projects (id, email, settings) values (?, ?, ?);"
	with sqlite3.connect(db_filename) as conn:
		result = conn.execute(select_query, (id,))
		count = next(iter(next(result)))
		if count > 0:
			conn.execute(update_query, (settings, id) )
		else:
			conn.execute(insert_query, (id, email, settings) )
	
def retrieve(id):
	query = "SELECT settings FROM projects WHERE id=?;"
	with sqlite3.connect(db_filename) as conn:
		results = conn.execute(query, (id,))
	result = next(iter(next(results)))
	return json.loads(result)

def delete(id):
	query = "DELETE FROM projects WHERE id=?;"
	with sqlite3.connect(db_filename) as conn:
		conn.execute(query, (id,))

def main():
	if not os.path.exists(db_filename):
		print db_filename, 'not found. Generating...'
		create_schema()
	else:
		print 'Database exists, assume schema does, too.'

def create_schema():
	schema_query = """
		CREATE TABLE projects (
			id text primary key,
			email text,
			settings text
		);
	"""
	with sqlite3.connect(db_filename) as conn:
		conn.execute(schema_query)
		conn.execute("""
			insert into projects (id, email, settings)
			values ('marks-project', 'mark@eateggs.com', '{ "setting":"value" }');
			""")
	print 'schema created'

if __name__ == "__main__":
	main()
