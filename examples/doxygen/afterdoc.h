/*! A test class */

class Test1
{
  public:
    /** An enum type. 
     *  The documentation block cannot be put after the enum! 
     */
    enum EnumType
    {
      int EVal1,     /**< enum value 1 */
      int EVal2      /**< enum value 2 */
    };

    /// Nested struct right here
    struct Nested {
      /// I'm also here
      bool enabled;
    };

    void member();   //!< a member function.
    
  protected:
    int value;       /*!< an integer value */
};
