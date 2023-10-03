#[derive(Debug, PartialEq)]
pub struct StatusResult {
    status: Status,
}

#[derive(Debug, PartialEq)]
pub enum Status {
    Ok,
    Err(String),
}
