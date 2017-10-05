extern crate rust_base58;

/*use rust_base58::{ToBase58, FromBase58};

fn main() {
    let x = &[1, 2, 3];

    // to_base58() returns a String
    let x_b58 = x.to_base58();
    assert_eq!("Ldp", x_b58);

    // from_base58() returns a Vec<u8>
    let x_again = x_b58.from_base58().unwrap();
    assert_eq!(x, &x_again[..]);

    // from_base58() can fail, for example due to the input string
    // containing an invalid base58 character like "I":
    assert!("I".from_base58().is_err());
}
*/