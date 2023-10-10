use rand::{distributions::Alphanumeric, Rng};
use std::{thread, time::Duration};

pub fn sleep(millis: u64) {
    thread::sleep(Duration::from_millis(millis));
}

pub fn rand_string() -> String {
    rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(12)
        .map(char::from)
        .collect()
}
