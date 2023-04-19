class EmptyData(Exception):
    msg: str = "Empty data."


class FailToCommit(Exception):
    msg: str = "Fail to commit data into DB."
