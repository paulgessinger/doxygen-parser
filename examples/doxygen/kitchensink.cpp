/// A struct
struct Struct {
  /// a variable
  int variable;

  /// A nested struct
  struct Nested {
    /// A nested struct variable
    bool variable;
  };

  /// A nested enum
  enum NestedEnum {
    int val1, ///< val1 of enum
    int val2 ///< val2 of enum
  };


  public:
  /// A public method
  /// @param arg An argument
  bool public_method(double arg) const;

  protected:
  /// A protected method
  int protected_method(bool arg);
  /// A protected const method
  int protected_method_const(bool arg) const;

  private:
  /// A private method
  int private_method(bool arg);
  /// A private const method
  int private_method_const(bool arg) const;
};

/// A global function
int global_function(bool flag);
  
/// A global enum
enum GlobalEnum {
  int val1,
  int val2
};

/// I am a namespace
namespace NS1 {
  /// I am a namespaced function
  int namespaced_function(bool arg);

  /// I am a namespaced class
  class Class2 {
    /// Another member
    void init();

    /// More nesting
    struct AnotherNested {
      /// limit variable
      double limit;
    };
  };
}
