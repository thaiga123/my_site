from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__, static_folder="static")
app.secret_key = "your_secret_key"  # Replace with a secure secret key

BLOGS_FILE = "blogs.json"
ADMIN_PASSWORD = "V3@6y@j1"  # Replace with a secure password

# Load blogs
def load_blogs():
    try:
        with open(BLOGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save blogs
def save_blogs(blogs):
    with open(BLOGS_FILE, "w") as f:
        json.dump(blogs, f, indent=4)

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("blogs"))
        else:
            flash("Invalid password!", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("blogs"))

@app.route("/blogs", methods=["GET", "POST"])
def blogs():
    blogs = load_blogs()
    is_admin = session.get("admin", False)

    if request.method == "POST" and is_admin:
        # Admin functionality: create a new blog
        title = request.form.get("title")
        content = request.form.get("content")
        if title and content:
            new_blog = {
                "id": len(blogs) + 1,
                "title": title,
                "content": content.replace("\n", "<br>"),  # Handle line breaks
                "likes": 0,
                "comments": []
            }
            blogs.append(new_blog)
            save_blogs(blogs)
        flash("New blog added successfully!", "success")
        return redirect(url_for("blogs"))

    return render_template("blogs.html", blogs=blogs, is_admin=is_admin)

@app.route("/blogs/<int:blog_id>", methods=["GET", "POST"])
def blog_detail(blog_id):
    blogs = load_blogs()
    blog = next((b for b in blogs if b["id"] == blog_id), None)

    if not blog:
        return "Blog not found", 404

    if request.method == "POST":
        if "like" in request.form:
            blog["likes"] += 1
        elif "comment" in request.form:
            comment = request.form.get("comment")
            if comment:
                blog["comments"].append(comment)
        save_blogs(blogs)
        flash("Action successful!", "success")
        return redirect(url_for("blog_detail", blog_id=blog_id))

    return render_template("blog_detail.html", blog=blog)

@app.route("/blogs/delete/<int:blog_id>")
def delete_blog(blog_id):
    if not session.get("admin"):
        return "Unauthorized", 403

    blogs = load_blogs()
    blogs = [b for b in blogs if b["id"] != blog_id]
    save_blogs(blogs)
    flash("Blog deleted successfully!", "success")
    return redirect(url_for("blogs"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
