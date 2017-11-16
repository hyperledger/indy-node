///   Copyright 2017 Sovrin Foundation
///
///   Licensed under the Apache License, Version 2.0 (the "License");
///   you may not use this file except in compliance with the License.
///   You may obtain a copy of the License at
///
///       http://www.apache.org/licenses/LICENSE-2.0
///
///   Unless required by applicable law or agreed to in writing, software
///   distributed under the License is distributed on an "AS IS" BASIS,
///   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
///   See the License for the specific language governing permissions and
///   limitations under the License.
///

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