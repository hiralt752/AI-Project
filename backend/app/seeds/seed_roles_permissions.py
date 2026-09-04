import os

from sqlalchemy import select

from app.core.security import hash_password
from app.database.connection import SessionLocal
# Import the package instead of individual model modules.  Its initializer loads
# every ORM model, so SQLAlchemy can resolve relationships such as Role.users.
from app.models import Permission, Role, RolePermission, User


ROLES = [
    {
        "name": "Admin",
        "description": "Administrator with full system access",
    },
    {
        "name": "User",
        "description": "Regular application user",
    },
]


PERMISSIONS = [
    {
        "name": "image.analyze",
        "description": "Analyze images using AI",
    },
    {
        "name": "image.ocr",
        "description": "Extract text from images using OCR",
    },
    {
        "name": "image.detect",
        "description": "Detect objects in images",
    },
    {
        "name": "document.summarize",
        "description": "Summarize uploaded documents",
    },
]


ADMIN_USER = {
    "name": os.getenv("SEED_ADMIN_NAME", "Jaimi Admin"),
    "email": os.getenv("SEED_ADMIN_EMAIL"),
    "password": os.getenv("SEED_ADMIN_PASSWORD"),
}


def seed_roles():
    db = SessionLocal()

    try:
        for role_data in ROLES:

            existing_role = db.scalar(
                select(Role).where(
                    Role.name == role_data["name"],
                    Role.is_deleted == False,
                )
            )

            if not existing_role:
                role = Role(**role_data)
                db.add(role)

        db.commit()

        print("Roles seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def seed_permissions():
    db = SessionLocal()

    try:
        for permission_data in PERMISSIONS:

            existing_permission = db.scalar(
                select(Permission).where(
                    Permission.name == permission_data["name"],
                    Permission.is_deleted == False,
                )
            )

            if not existing_permission:
                permission = Permission(**permission_data)
                db.add(permission)

        db.commit()

        print("Permissions seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def seed_role_permissions():
    db = SessionLocal()

    try:
        admin = db.scalar(
            select(Role).where(
                Role.name == "Admin",
                Role.is_deleted == False,
            )
        )

        user = db.scalar(
            select(Role).where(
                Role.name == "User",
                Role.is_deleted == False,
            )
        )

        permissions = db.scalars(
            select(Permission).where(
                Permission.is_deleted == False
            )
        ).all()

        if not admin or not user:
            raise Exception("Roles not found.")

        for permission in permissions:

            # Admin gets every permission
            existing_admin_permission = db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == admin.id,
                    RolePermission.permission_id == permission.id,
                    RolePermission.is_deleted == False,
                )
            )

            if not existing_admin_permission:
                db.add(
                    RolePermission(
                        role_id=admin.id,
                        permission_id=permission.id,
                    )
                )

            # User gets application permissions
            existing_user_permission = db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == user.id,
                    RolePermission.permission_id == permission.id,
                    RolePermission.is_deleted == False,
                )
            )

            if not existing_user_permission:
                db.add(
                    RolePermission(
                        role_id=user.id,
                        permission_id=permission.id,
                    )
                )

        db.commit()

        print("Role permissions seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def seed_admin_user():
    db = SessionLocal()

    try:
        if not ADMIN_USER["email"] or not ADMIN_USER["password"]:
            raise ValueError(
                "Set SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD before seeding the admin user."
            )

        admin_role = db.scalar(
            select(Role).where(
                Role.name == "Admin",
                Role.is_deleted == False,
            )
        )

        if not admin_role:
            raise Exception("Admin role not found.")

        existing_admin = db.scalar(
            select(User).where(
                User.email == ADMIN_USER["email"],
                User.is_deleted == False,
            )
        )

        if existing_admin:
            print("Admin user already exists; skipping.")
            return

        db.add(
            User(
                name=ADMIN_USER["name"],
                email=ADMIN_USER["email"],
                password_hash=hash_password(ADMIN_USER["password"]),
                role_id=admin_role.id,
            )
        )
        db.commit()
        print("Admin user seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def main():
    print("Starting seed...")

    seed_roles()
    seed_permissions()
    seed_role_permissions()
    seed_admin_user()

    print("Seed completed successfully.")


if __name__ == "__main__":
    main()
