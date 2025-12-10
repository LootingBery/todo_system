from datetime import datetime
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    deadline = db.Column(db.DateTime, nullable=True)

    def is_overdue(self):
        return self.deadline and datetime.now() > self.deadline

    def __repr__(self):
        return f"<Todo {self.id}>"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form["content"]
        deadline_raw = request.form.get("deadline")

        deadline = (
            datetime.fromisoformat(deadline_raw)
            if deadline_raw else None
        )

        new_task = Todo(
            content=content,
            deadline=deadline
        )

        db.session.add(new_task)
        db.session.commit()
        return redirect("/")

    tasks = Todo.query.order_by(
        Todo.deadline.is_(None),
        Todo.deadline,
        Todo.date_created
    ).all()

    return render_template("index.html", tasks=tasks)


@app.route("/delete/<int:id>")
def delete(id):
    task = Todo.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect("/")




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
