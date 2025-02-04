# class ErrorCode:

from sqlmodel import Session, select

from app.ddd.domain import (
    User,
    UserDuplicationError,
    UserId,
    UserNotFoundError,
    UserRepository,
    UserUpdateConflictError,
    # UserReportDuplicationError,
)
from migrations.models import TUser, TUserReport


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: Session) -> None:
        self.__session: Session = session

    def _fetch_by_id(self, _id: str) -> TUser | None:
        statement = select(TUser).where(TUser.user_id == _id)
        return self.__session.exec(statement).first()

    def _fetch_user_report_by_id(self, _id: str) -> TUserReport | None:
        statement = select(TUserReport).where(TUserReport.user_report_id == _id)
        return self.__session.exec(statement).first()

    def _apply(self, model: TUser | TUserReport) -> None:
        self.__session.add(model)

    def _delete(self, model: TUser) -> None:
        self.__session.delete(model)

    def find_by_id(self, _id: UserId) -> User:
        model: TUser | None = self._fetch_by_id(_id.root)
        if model is None:
            raise UserNotFoundError(_id.root)
        return User.model_validate(model)

    def insert(self, user: User) -> None:
        model: TUser | None = self._fetch_by_id(user.user_id)
        if model is not None: # 重複判定
            raise UserDuplicationError(user.user_id)
        model = TUser.model_validate(user.model_dump(exclude={"created_at", "updated_at"})) # 新規作成
        self._apply(model)

    def insert_user_report(self, user: User) -> None:
        for user_report in user.user_reports:
            _id = user_report.user_report_id
            model: TUserReport | None = self._fetch_user_report_by_id(_id)
            print(_id)
            print(model)
            if model is not None: # 重複判定
                # raise UserReportDuplicationError(_id)
                continue
            model = TUserReport.model_validate(user_report.model_dump(exclude={"created_at", "updated_at"})) # 新規作成
            self._apply(model)

    def update(self, user: User) -> None:
        model: TUser | None = self._fetch_by_id(user.user_id)
        if model is None: # ない場合更新できない 現在のユースケースでは基本的に発生しない
            raise UserNotFoundError(user.user_id)
        if user.updated_at != model.updated_at: # 更新日検証による楽観的ロックの確認
            raise UserUpdateConflictError(user_id=user.user_id)
        model.sqlmodel_update(user.model_dump(exclude={"created_at", "updated_at", "user_reports"})) # 更新データの統合
        self._apply(model)

    def delete(self, _id: UserId) -> None:
        model: TUser | None = self._fetch_by_id(_id.root)
        if model is None:
            raise UserNotFoundError(_id.root)

        # TODO(nonomura): 論理削除する場合
        # model.updated_at = datetime.now()
        # model.deleted_at = datetime.now() # 論理削除する場合
        # self._apply(model)

        self._delete(model) # 物理削除用

    def query(self) -> list[User]:
        """TODO(nonomura): 検索条件整理後に整理。必要に応じてクエリサービスに分ける."""
        models: list[TUser] = self.__session.query(TUser).all()
        return [User.model_validate(model) for model in models]

