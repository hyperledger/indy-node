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

  string public constant regex = "did:(indy2|indy|sov):([a-zA-Z0-9]+:)+([1-9A-HJ-NP-Za-km-z]{22}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})";

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
    if (c == 48) {
      return State(false, s18);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s19);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s20);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s18(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s22);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 90 || c >= 103 && c <= 122) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s19(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s22);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s25);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s26);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s20(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s26);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s21(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s24);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s22(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s27);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 90 || c >= 103 && c <= 122) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s23(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s18);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s19);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s20);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s21);
    }

    return State(false, s0);
  }

  function s24(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s24);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s25(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s27);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s28);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s29);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s26(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s29);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s27(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s30);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 90 || c >= 103 && c <= 122) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s28(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s30);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s31);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s32);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s29(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s32);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s30(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s33);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 90 || c >= 103 && c <= 122) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s31(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s33);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s34);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s35);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s32(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s35);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s33(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s36);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 90 || c >= 103 && c <= 122) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s34(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s36);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s37);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s38);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s35(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s38);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s36(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s39);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 90 || c >= 103 && c <= 122) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s37(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s39);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s40);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s41);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s38(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s41);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s39(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s42);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 90 || c >= 103 && c <= 122) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s40(uint8 c) pure internal returns (State memory) {
    if (c == 48) {
      return State(false, s42);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s43);
    }
    if (c == 58) {
      return State(false, s23);
    }
    if (c >= 71 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 103 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s44);
    }
    if (c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }

    return State(false, s0);
  }

  function s41(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s44);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s42(uint8 c) pure internal returns (State memory) {
    if (c == 45) {
      return State(false, s45);
    }
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s24);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s43(uint8 c) pure internal returns (State memory) {
    if (c == 45) {
      return State(false, s45);
    }
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s46);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s44(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s46);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s45(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s47);
    }

    return State(false, s0);
  }

  function s46(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s48);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s47(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s49);
    }

    return State(false, s0);
  }

  function s48(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s50);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s49(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s51);
    }

    return State(false, s0);
  }

  function s50(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s52);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s51(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s53);
    }

    return State(false, s0);
  }

  function s52(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s54);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s53(uint8 c) pure internal returns (State memory) {
    if (c == 45) {
      return State(false, s55);
    }

    return State(false, s0);
  }

  function s54(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s56);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s55(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s57);
    }

    return State(false, s0);
  }

  function s56(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s58);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s57(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s59);
    }

    return State(false, s0);
  }

  function s58(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s60);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s59(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s61);
    }

    return State(false, s0);
  }

  function s60(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s62);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s61(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s63);
    }

    return State(false, s0);
  }

  function s62(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s64);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s63(uint8 c) pure internal returns (State memory) {
    if (c == 45) {
      return State(false, s65);
    }

    return State(false, s0);
  }

  function s64(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s66);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s65(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s67);
    }

    return State(false, s0);
  }

  function s66(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s68);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s67(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s69);
    }

    return State(false, s0);
  }

  function s68(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(false, s70);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s69(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s71);
    }

    return State(false, s0);
  }

  function s70(uint8 c) pure internal returns (State memory) {
    if (c == 48 || c == 73 || c == 79 || c == 108) {
      return State(false, s24);
    }
    if (c >= 49 && c <= 57 || c >= 65 && c <= 72 || c >= 74 && c <= 78 || c >= 80 && c <= 90 || c >= 97 && c <= 107 || c >= 109 && c <= 122) {
      return State(true, s72);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s71(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s73);
    }

    return State(false, s0);
  }

  function s72(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 90 || c >= 97 && c <= 122) {
      return State(false, s24);
    }
    if (c == 58) {
      return State(false, s23);
    }

    return State(false, s0);
  }

  function s73(uint8 c) pure internal returns (State memory) {
    if (c == 45) {
      return State(false, s74);
    }

    return State(false, s0);
  }

  function s74(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s75);
    }

    return State(false, s0);
  }

  function s75(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s76);
    }

    return State(false, s0);
  }

  function s76(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s77);
    }

    return State(false, s0);
  }

  function s77(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s78);
    }

    return State(false, s0);
  }

  function s78(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s79);
    }

    return State(false, s0);
  }

  function s79(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s80);
    }

    return State(false, s0);
  }

  function s80(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s81);
    }

    return State(false, s0);
  }

  function s81(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s82);
    }

    return State(false, s0);
  }

  function s82(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s83);
    }

    return State(false, s0);
  }

  function s83(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s84);
    }

    return State(false, s0);
  }

  function s84(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(false, s85);
    }

    return State(false, s0);
  }

  function s85(uint8 c) pure internal returns (State memory) {
    if (c >= 48 && c <= 57 || c >= 65 && c <= 70 || c >= 97 && c <= 102) {
      return State(true, s0);
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
