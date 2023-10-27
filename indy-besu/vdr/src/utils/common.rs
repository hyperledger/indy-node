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
