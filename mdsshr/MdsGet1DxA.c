/*  CMS REPLACEMENT HISTORY, Element MdsGet1DxA.C */
/*  *13    5-AUG-1996 14:38:14 TWF "Fix copy_dx for unpacked descriptors" */
/*  *12    2-AUG-1996 12:28:46 TWF "fix alignment" */
/*  *11    2-AUG-1996 08:16:18 TWF "Use int instead of long" */
/*  *10   19-OCT-1995 15:01:01 TWF "Add mdsxdroutines.c" */
/*  *9    18-OCT-1994 16:38:38 TWF "No longer support VAXC" */
/*  *8     1-MAR-1993 08:41:36 TWF "Use standard indentation" */
/*  *7    26-FEB-1993 16:49:33 TWF "Use MDSSHR" */
/*  *6     9-FEB-1993 09:56:18 TWF "Use DECC" */
/*  *5     8-FEB-1993 16:16:54 TWF "Use DECC" */
/*  *4     3-FEB-1993 11:11:29 TWF "Make it portable" */
/*  *3    30-DEC-1992 11:34:45 TWF "Make it portable" */
/*  *2     1-MAY-1991 19:46:52 KLARE "Handle CLASS_CA's input, fix A0" */
/*  *1    28-DEC-1989 10:39:01 TWF "Get 1 XD pointing to an array" */
/*  CMS REPLACEMENT HISTORY, Element MdsGet1DxA.C */
/*------------------------------------------------------------------------------

		Name: MdsGet1DxA

		Type:   C function

		Author:	Thomas W. Fredian
			MIT Plasma Fusion Center

		Date:    8-SEP-1988

		Purpose: Get an XD pointing to an array descriptor
			 Used by CVT_DX_DX_A.

------------------------------------------------------------------------------

	Call sequence:

    status = MdsGet1DxA(in_dsc,length_ptr,dtype_ptr,out_xd);

------------------------------------------------------------------------------
   Copyright (c) 1988
   Property of Massachusetts Institute of Technology, Cambridge MA 02139.
   This program cannot be copied or distributed in any form for non-MIT
   use without specific written approval of MIT Plasma Fusion Center
   Management.
---------------------------------------------------------------------------

	Description:


+-----------------------------------------------------------------------------*/

#define _DESCRIPTOR_PREFIXES
#include <stdlib.h>
#include <mdsdescrip.h>
#include <mdsshr.h>

#define align(bytes,size) ((((bytes) + (size) - 1)/(size)) * (size))

static char *cvsrev = "@(#)$RCSfile$ $Revision$ $Date$";

  int       MdsGet1DxA(struct descriptor_a * in_ptr, unsigned short *length_ptr, unsigned char *dtype_ptr,
			            struct descriptor_xd *out_xd)
{
  array_coeff *in_dsc = (array_coeff *) in_ptr;
  int       new_arsize;
  int       dsc_size;
  unsigned int new_size;
  int       status;
  int       i;
  int align_size;
  array_coeff *out_dsc;
  unsigned char dsc_dtype = DTYPE_DSC;
  new_arsize = (in_dsc->dscL_arsize / in_dsc->dscW_length) * (*length_ptr);
  dsc_size = sizeof(struct descriptor_a) + (in_dsc->aflags.dscV_coeff ? sizeof(char *) + 
                                                          sizeof(int) * in_dsc->dscB_dimct : 0) +
						 (in_dsc->aflags.dscV_bounds ? sizeof(int) * (in_dsc->dscB_dimct * 2) 
                                                                                                     : 0);
  align_size = (*dtype_ptr == DTYPE_T) ? 1 : *length_ptr;
  dsc_size = align(dsc_size,align_size);
  new_size = dsc_size + new_arsize;
  status = MdsGet1Dx(&new_size, &dsc_dtype, out_xd, NULL);
  if (status & 1)
  {
    out_dsc = (array_coeff *) out_xd->dscA_pointer;
    *(struct descriptor_a *) out_dsc = *(struct descriptor_a *) in_dsc;
    out_dsc->dscW_length = *length_ptr;
    out_dsc->dscB_dtype = *dtype_ptr;
    out_dsc->dscA_pointer = (char *) out_dsc + align(dsc_size,align_size);
    out_dsc->dscL_arsize = new_arsize;
    if (out_dsc->aflags.dscV_coeff)
    {
      if (out_dsc->dscB_class == CLASS_CA)
      {
        int offset = ((int) out_dsc->dscW_length) * ((in_dsc->dscA_a0 - (char *)0) / ((int) in_dsc->dscW_length));
	out_dsc->dscA_a0 = out_dsc->dscA_pointer + offset;
      }
      else
      {
        int offset = ((int) out_dsc->dscW_length) *
		       ((in_dsc->dscA_a0 - in_dsc->dscA_pointer) / ((int) in_dsc->dscW_length));
	out_dsc->dscA_a0 = out_dsc->dscA_pointer + offset;
      }
      for (i = 0; i < out_dsc->dscB_dimct; i++)
	out_dsc->dscL_m[i] = in_dsc->dscL_m[i];
      if (in_dsc->aflags.dscV_bounds)
      {
	struct bound
	{
	  int       l;
	  int       u;
	};
	struct bound *new_bound_ptr = (struct bound *) & out_dsc->dscL_m[out_dsc->dscB_dimct];
	struct bound *a_bound_ptr = (struct bound *) & in_dsc->dscL_m[in_dsc->dscB_dimct];
	for (i = 0; i < out_dsc->dscB_dimct; i++)
	  new_bound_ptr[i] = a_bound_ptr[i];
      }
    }
    out_dsc->dscB_class = CLASS_A;
  }
  return status;
}
