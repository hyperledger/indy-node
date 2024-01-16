#[cfg(test)]
use rand::{distributions::Alphanumeric, Rng, RngCore};

#[cfg(test)]
pub fn rand_string() -> String {
    rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(12)
        .map(char::from)
        .collect()
}

#[cfg(test)]
pub fn rand_bytes() -> Vec<u8> {
    let mut data = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut data);
    data.to_vec()
}

#[cfg(test)]
pub fn init_env_logger() {
    let _ = env_logger::builder().is_test(true).try_init();
}
