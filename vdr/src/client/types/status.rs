#[derive(Debug, PartialEq)]
pub struct StatusResult {
    pub status: Status,
}

#[derive(Debug, PartialEq)]
pub enum Status {
    Ok,
    Err(String),
}
