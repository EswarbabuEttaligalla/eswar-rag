from app.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, session):
        self.user_repo = UserRepository(session)

    async def get_user(self, user_id):
        return await self.user_repo.get(user_id)

    async def list_users(self):
        return await self.user_repo.list()
