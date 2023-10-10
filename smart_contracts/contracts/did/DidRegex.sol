// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * Generated using https://github.com/gnidan/solregex
 */
library DidRegex {
  struct State {
    bool accepts;
    function (uint8) pure internal returns (State memory) func;
  }

  string public constant regex = "did:(indy2|indy|sov):([a-zA-Z0-9]+:)+[1-9A-HJ-NP-Za-km-z]{21,22}";

  function s0(uint8 c) pure internal returns (State memory) {
    // silence unused var warning
    c = c;
    
    return State(false, s0);
  }

  function s1(uint8 c) pure internal returns (State memory) {
    if (c == 100) {
      return State(false, s2);
    }

    return State(false, s0);
  }

  function s2(uint8 c) pure internal returns (State memory) {
    if (c == 105) {
      return State(false, s3);
    }

    return State(false, s0);
  }

  function s3(uint8 c) pure internal returns (State memory) {
    if (c == 100) {
      return State(false, s4);
    }

    return State(false, s0);
  }

  function s4(uint8 c) pure internal returns (State memory) {
    if (c == 58) {
      return State(false, s5);
    }

    return State(false, s0);
  }

  function s5(uint8 c) pure internal returns (State memory) {
    if (c == 105) {
      return State(false, s6);
    }
    if (c == 115) {
      return State(false, s7);
    }

    return State(false, s0);
  }

  function s6(uint8 c) pure internal returns (State memory) {
    if (c == 110) {
      return State(false, s8);
    }

    return State(false, s0);
  }

  function s7(uint8 c) pure internal returns (State memory) {
    if (c == 111) {
      return State(false, s9);
    }

    return State(false, s0);
  }

  function s8(uint8 c) pure internal returns (State memory) {
    if (c == 100) {
      return State(false, s10);
    }

    return State(false, s0);
  }

  function s9(uint8 c) pure internal returns (State memory) {
    if (c == 118) {
      return State(false, s11);
    }

    return State(false, s0);
  }

  function s10(uint8 c) pure internal returns (State memory) {
    if (c == 121) {
      return State(false, s12);
    }

    return State(false, s0);
  }

  function s11(uint8 c) pure internal returns (State memory) {
    if (c == 58) {
      return State(false, s13);
    }

    return State(false, s0);
  }

  function s12(uint8 c) pure internal returns (State memory) {
    if (c == 50) {
      return State(false, s14);
    }
    if (c == 58) {
      return State(false, s13);
    }

    return State(false, s0);
  }

  function s13(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s15);
    }

    return State(false, s0);
  }

  function s14(uint8 c) pure internal returns (State memory) {
    if (c == 58) {
      return State(false, s13);
    }

    return State(false, s0);
  }

  function s15(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s16);
    }
    if (c == 58) {
      return State(false, s17);
    }

    return State(false, s0);
  }

  function s16(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s16);
    }
    if (c == 58) {
      return State(false, s17);
    }

    return State(false, s0);
  }

  function s17(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s18);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s19);
    }

    return State(false, s0);
  }

  function s18(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s20);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s19(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s22);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s20(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s20);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s21(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s18);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s19);
    }

    return State(false, s0);
  }

  function s22(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s23);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s23(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s24);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s24(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s25);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s25(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s26);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s26(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s27);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s27(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s28);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s28(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s29);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s29(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s30);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s30(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s31);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s31(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s32);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s32(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s33);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s33(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s34);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s34(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s35);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s35(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s36);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s36(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s37);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s37(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s38);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s38(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s39);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s39(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s40);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s40(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(true, s41);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s41(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s20);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(true, s42);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s42(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s20);
    }
    if (c == 58) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function matches(string memory input) public pure returns (bool) {
    State memory cur = State(false, s1);

    for (uint i = 0; i < bytes(input).length; i++) {
      uint8 c = uint8(bytes(input)[i]);

      cur = cur.func(c);
    }

    return cur.accepts;
  }
}
